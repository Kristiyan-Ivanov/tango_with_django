from django.test import TestCase
from rango.models import Category, Page
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from time import sleep


class CategoryModelTests(TestCase):

    def test_ensure_views_are_positive(self):
        """
        Ensures the number of views for a Category are positive or zero.
        """
        category = Utilities.add_category('test', -1)

        self.assertEqual((category.views >= 0), True)

    def test_slug_line_creation(self):
        """
        Checks to make sure that when a category is created, an
        appropriate slug is created.
        Example: "Random Category String" should be "random-category-string".
        """
        category = Utilities.add_category("Random Category String")

        self.assertEqual(category.slug, 'random-category-string')


class PageModelTests(TestCase):

    def test_last_visited_not_in_future(self):
        """
        Checks if last_visited attribute of the Page model
        can be set to a datetime in the future
        """
        category = Utilities.add_category('Python', 1, 1)
        page = Utilities.add_page("Python Tutorial", 'https://www.python.org/', category)
        page.last_visited = page.last_visited + timedelta(days=3)
        page.save()

        self.assertLessEqual(page.last_visited, now())

    def test_last_visited_parameter_updated_on_page_visit(self):
        """
        Ensures that the last_visited parameter of the Page model is updated
        every time a user requests a page.
        """
        category = Utilities.add_category('Python')
        page = Utilities.add_page("Python Tutorial", 'https://www.python.org/', category)
        page_creation_time = page.last_visited

        self.client.get(reverse('rango:goto'), {'page_id': page.id})
        page.refresh_from_db()

        self.assertGreater(page.last_visited, page_creation_time)


class IndexViewTests(TestCase):

    def test_index_view_with_no_categories(self):
        """
        Checks that the appropriate message is returned to the user
        if no categories exist.
        """
        response = self.client.get(reverse('rango:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no categories present.')
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        """
        Tests if an appropriate index view is returned when categories are present.
        """
        Utilities.add_category('Python', 1, 1)
        Utilities.add_category('C++', 1, 1)
        Utilities.add_category('Java', 1, 1)

        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'C++')
        self.assertContains(response, 'Java')

        num_categories = len(response.context['categories'])
        self.assertEqual(num_categories, 3)


class Utilities:

    @staticmethod
    def add_category(name, views=0, likes=0):
        category = Category.objects.get_or_create(name=name)[0]
        category.views = views
        category.likes = likes
        category.save()

        return category

    @staticmethod
    def add_page(title, url, category, views=0):
        page = Page.objects.get_or_create(title=title, url=url, category=category)[0]
        page.views = views
        page.save()

        return page
