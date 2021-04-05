from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page, UserProfile
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from rango.forms import CategoryForm, PageForm, UserProfileForm
from django.views.generic import TemplateView
from datetime import datetime
from rango.bing_search import BingSearch
from django.http import HttpResponse


class IndexView(TemplateView):

    def get(self, request):
        # Query the database for a list of ALL categories currently stored.
        # Order the categories by the number of likes in descending order.
        # Retrieve the top 5 only -- or all if less than 5.
        # Place the list in our context_dict dictionary (with our boldmessage!)
        # that will be passed to the template engine.
        category_list = Category.objects.order_by('-likes')[:5]

        # list with top 5 most viewed pages
        pages_list = Page.objects.order_by('-views')[:5]

        context_dict = dict()
        context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
        context_dict['categories'] = category_list
        context_dict['pages'] = pages_list

        # Helper function to handle cookies
        visitor_cookie_handler(request)

        return render(request, 'rango/index.html', context=context_dict)


class AboutView(TemplateView):

    def get(self, request):
        context_dict = {'boldmessage': 'Kristiyan Ivanov'}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request, 'rango/about.html', context=context_dict)


class ShowCategoryView(TemplateView):

    def generate_context_dict(self, category_name_slug):
        context_dict = dict()

        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['category'] = category
            context_dict['pages'] = pages

        except Category.DoesNotExist:
            context_dict['category'] = None
            context_dict['pages'] = None

        return context_dict

    def get(self, request, category_name_slug):
        context_dict = self.generate_context_dict(category_name_slug)
        return render(request, 'rango/category.html', context=context_dict)

    def post(self, request, category_name_slug):
        context_dict = self.generate_context_dict(category_name_slug)

        query = request.POST['query'].strip()
        results = BingSearch.run_query(query)
        context_dict['query'] = query
        context_dict['result_list'] = results

        return render(request, 'rango/category.html', context=context_dict)


class CategorySuggestionView(TemplateView):

    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''

        category_list = get_category_list(max_results=8, starts_with=suggestion)

        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')

        return render(request, 'rango/categories.html', {'categories': category_list})


def get_category_list(max_results=0, starts_with=''):
    category_list = []
    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]

    return category_list


class AddCategoryView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid():
            cat = form.save(commit=True)

            # confirmation that the category is added
            print(cat, cat.slug)

            return redirect(reverse('rango:index'))
        else:
            # print form contained errors to the terminal
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})


class LikeCategoryView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)

        category.likes = category.likes + 1
        category.save()
        return HttpResponse(category.likes)


class AddPageView(TemplateView):

    def get_category(self, category_name_slug):
        try:
            return Category.objects.get(slug=category_name_slug)

        except Category.DoesNotExist:
            return None

    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        category = self.get_category(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        form = PageForm()

        return render(request, 'rango/add_page.html', {'form': form, 'category': category})

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        category = self.get_category(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            return redirect(reverse('rango:show_category',
                                    kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)


class RegisterProfileView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        return render(request, 'rango/profile_registration.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            # confirmation that the category is added
            print(user_profile.user.username)

            return redirect(reverse('rango:index'))
        else:
            # print form contained errors to the terminal
            print(form.errors)

        return render(request, 'rango/profile_registration.html', {'form': form})


class ProfileView(TemplateView):

    def get_user_details(username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({
            'website': user_profile.website,
            'picture': user_profile.picture
        })

        return user, user_profile, form

    @method_decorator(login_required)
    def get(self, request, username):
        try:
            user, user_profile, form = self.get_user_details(username)
        except TypeError:
            redirect(reverse('rango:index'))

        context_dict = {
            'user_profile': user_profile,
            'selected_user': user,
            'form': form
        }

        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, username):
        try:
            user, user_profile, form = self.get_user_details(username)
        except TypeError:
            redirect(reverse('rango:index'))

        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:profile', kwargs={'username': username}))

        context_dict = {
            'user_profile': user_profile,
            'selected_user': user,
            'form': form
        }

        return render(request, 'rango/profile.html', context_dict)


class ListUsersView(TemplateView):

    def get(self, request):
        users = UserProfile.objects.filter(user__is_staff=False).order_by('user__username')
        context_dict = {'users': users}

        return render(request, 'rango/users.html', context_dict)


class AddBingSearchPageView(TemplateView):

    @method_decorator(login_required)
    def get(self, request):
        url = request.GET['page_url']
        title = request.GET['title']
        category_id = request.GET['category_id']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')

        page, just_created = Page.objects.get_or_create(url=url, category=category)
        if just_created:
            page.title = title
            page.save()

        pages = Page.objects.filter(category_id=category_id).order_by('-views')
        return render(request, 'rango/list_pages.html', {'pages': pages})


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val

    return val


# wrapper view used to track external redirects
def goto_page(request):
    page_id = request.GET.get('page_id')

    try:
        selected_page = Page.objects.get(id=page_id)
    except Page.DoesNotExist:
        return redirect(reverse('rango:index'))

    selected_page.views = selected_page.views + 1
    selected_page.save()

    return redirect(selected_page.url)


# Helper function counting visits
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


""" DEPRECATED """

# view responsible for the Bing search functionality
# def search(request):
#     result_list = list()
#     query = ''
#
#     if request.method == 'POST':
#         query = request.POST['query'].strip()
#         if query:
#             # Run Bing function to get the results list!
#             result_list = run_query(query)
#
#     return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})
