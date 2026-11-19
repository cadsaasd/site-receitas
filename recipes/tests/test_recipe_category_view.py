from django.urls import resolve, reverse
from recipes import views
from .test_recipe_base import RecipeTestBase
from unittest.mock import patch
from recipes.models import Recipe


class RecipeCategoryViewTest(RecipeTestBase):
    def test_recipe_category_view_function_is_correct(self):
        view = resolve(
            reverse('recipes:category', kwargs={'category_id': 1})
        )
        self.assertIs(view.func, views.category)

    def test_recipe_category_view_return_404_if_no_recipes_found(self):
        response = self.client.get(
            reverse('recipes:category', kwargs={'category_id': 1000})
        )
        self.assertEqual(response.status_code, 404)

    def test_recipe_home_category_loads_recipes(self):
        needed_title = 'This is a category test'
        # Needs a recipe for this test
        self.make_recipe(title=needed_title)

        response = self.client.get(reverse("recipes:category", args=(1,)))
        content = response.content.decode('utf-8')

        # Check if one recipe exists
        self.assertIn(needed_title, content)

    def test_recipe_category_template_dont_load_recipes_not_published(self):
        # Needs a recipe for this test
        recipe = self.make_recipe(is_published=False)

        response = self.client.get(
            reverse(
                'recipes:category',
                kwargs={
                    'category_id': recipe.category.id,
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_recipe_category_is_paginated(self):
        category = self.make_category(name='Category')

        for i in range(8):
            kwargs = {'slug': f'r{i}',
                      'author_data': {'username': f'u{i}'},
                      }
            self.make_recipe(**kwargs)

        Recipe.objects.all().update(category=category)
        with patch('recipes.views.PER_PAGES', new=3):
            response = self.client.get(
                reverse(
                    'recipes:category',
                    kwargs={
                        'category_id': category.id,
                    },
                )
            )
            recipes = response.context['recipes']
            paginator = recipes.paginator

            self.assertEqual(paginator.num_pages, 3)
            self.assertEqual(len(paginator.get_page(1)), 3)
            self.assertEqual(len(paginator.get_page(2)), 3)
            self.assertEqual(len(paginator.get_page(3)), 2)
