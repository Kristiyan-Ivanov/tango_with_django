from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]

    context_dict = dict()
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list

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
