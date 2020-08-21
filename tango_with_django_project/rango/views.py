from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
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

    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    context_dict = {'boldmessage': 'Kristiyan Ivanov'}

    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # Creates a context dictionary which we can
    # pass to the rendering engine.
    context_dict = {}

    try:
        # Gets category by category's slug
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all the associated pages
        pages = Page.objects.filter(category=category)

        # Adds pages and category to the context dictionary
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['Category'] = None
        context_dict['Page'] = None

    return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
    form = CategoryForm()

    # A HTTP POST ?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            cat = form.save(commit=True)

            # confirmation that the category is added
            print(cat, cat.slug)

            return redirect(reverse('rango:index'))
        else:
            # print form contained errors to the terminal
            print(form.errors)

    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                print(page.url)

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    # boolean value that tells the template whether the
    # registration was successful or not
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # saves the user to the database
            user = user_form.save()

            # hash and set password
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # checks if the user provided a picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            # Invalit form
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', context={'user_form': user_form,
                                                           'profile_form': profile_form,
                                                           'registered': registered})
