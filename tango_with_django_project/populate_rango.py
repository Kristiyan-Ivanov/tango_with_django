import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tango_with_django_project.settings')

import django

django.setup()
from rango.models import Category, Page


def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    python_pages = [
        {'title': 'Official Python Tutorial',
         'url': 'http://docs.python.org/3/tutorial/',
         'views': 12},
        {'title': 'How to Think like a Computer Scientist',
         'url': 'http://www.greenteapress.com/thinkpython/',
         'views': 24},
        {'title': 'Learn Python in 10 Minutes',
         'url': 'http://www.korokithakis.net/tutorials/python/',
         'views': 48}
    ]

    django_pages = [
        {'title': 'Official Django Tutorial',
         'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/',
         'views': 10},
        {'title': 'Django Rocks',
         'url': 'http://www.djangorocks.com/',
         'views': 20},
        {'title': 'How to Tango with Django',
         'url': 'http://www.tangowithdjango.com/',
         'views': 30}
    ]

    other_pages = [
        {'title': 'Bottle',
         'url': 'http://bottlepy.org/docs/dev/',
         'views': 15},
        {'title': 'Flask',
         'url': 'http://flask.pocoo.org',
         'views': 30}]

    cats = {'Python': {'pages': python_pages, 'views': 128, 'likes': 64},
            'Django': {'pages': django_pages, 'views': 64, 'likes': 32},
            'Other Frameworks': {'pages': other_pages, 'views': 32, 'likes': 16},
            'Pascal': {'pages': [], 'views': 0, 'likes': 0},
            'Perl': {'pages': [], 'views': 0, 'likes': 0},
            'PHP': {'pages': [], 'views': 0, 'likes': 0},
            'Prolog': {'pages': [], 'views': 0, 'likes': 0},
            'PostScript': {'pages': [], 'views': 0, 'likes': 0},
            'Programming': {'pages': [], 'views': 0, 'likes': 0}
            }

    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all the associated pages for that category.
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            if p:
                add_page(c, p['title'], p['url'], p['views'])

    # Print out the categories we have added.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print(f'- {c}: {p}')


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name, views, likes):
    category, just_created = Category.objects.get_or_create(name=name)
    if just_created:
        category.views = views
        category.likes = likes
        category.save()
    return category


# Start execution here!
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
