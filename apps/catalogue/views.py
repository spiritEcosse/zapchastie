from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView, \
    ProductDetailView as CoreProductDetailView
from django.utils.functional import cached_property
import logging
from apps.catalogue.models import Category, Feature
from django.http import HttpResponsePermanentRedirect, Http404
from django.utils.http import urlquote
from apps.catalogue.forms import ProductQuestionNgForm
from oscar.core.loading import get_class
from braces import views
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.views.generic import edit
from django.views.generic import detail
from django.views.generic import list
from django.core.mail import send_mail
from django.views.generic import FormView
import json
from apps.catalogue.reviews.forms import ReviewForm
from apps.catalogue.reviews.models import ProductReview
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

get_product_search_handler_class = get_class('catalogue.search_handlers', 'get_product_search_handler_class')

logger = logging.getLogger(__name__)


class ProductCategoryView(CoreProductCategoryView):
    feature_only = ('title', 'slug', 'parent__id', 'parent__title', )
    filter_slug = 'filter_slug'
    model_category = Category

    def get_category(self):
        category = super(ProductCategoryView, self).get_category()

        if not self.model_category.objects.filter(enable=True, pk=category.pk):
            raise Http404('"%s" does not exist' % self.request.get_full_path())
        return category

    def get(self, request, *args, **kwargs):
        self.kwargs['filter_slug_objects'] = self.selected_filters
        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    @cached_property
    def selected_filters(self):
        filter_slug = self.kwargs.get(self.filter_slug).split('/') if self.kwargs.get(self.filter_slug) else []
        features = Feature.objects.only(*self.feature_only).select_related('parent').filter(
            slug__in=filter_slug, level=1
        ).order_by('pk')

        if len(filter_slug) != features.count():
            raise Http404('"%s" does not exist' % self.request.get_full_path())

        return features

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            expected_path = category.get_absolute_url(self.kwargs)

            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_categories(self):
        """
        Return a list of the current category and its ancestors
        """
        return self.category.get_descendants(include_self=True)

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['url_extra_kwargs'] = {'category_slug': self.kwargs.get('category_slug')}
        context['selected_filters'] = self.selected_filters
        return context

    def get_search_handler(self, *args, **kwargs):
        kwargs['category'] = self.category
        kwargs['selected_filters'] = self.selected_filters
        return super(ProductCategoryView, self).get_search_handler(*args, **kwargs)


class ProductDetailView(CoreProductDetailView, FormView, views.JSONResponseMixin):
    form_class = ProductQuestionNgForm
    form_valid_message = unicode(_('You question has been sent!'))

    def get_object(self, queryset=None):
        self.kwargs['slug'] = self.kwargs['product_slug']
        return super(ProductDetailView, self).get_object()

    def get_queryset(self):
        return super(ProductDetailView, self).get_queryset().filter(enable=True).select_related(
            'product_class'
        ).prefetch_related(
            'filters__parent', 'stockrecords', 'images__original', 'product_class__options', 'recommended_products'
        )

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        initial_data = {}

        if self.request.user.is_authenticated():
            initial_data['name'] = self.request.user.username
            initial_data['email'] = self.request.user.email

        context['product_question_form'] = self.form_class(initial=initial_data)
        return context

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        return super(ProductDetailView, self).post(request, **kwargs)

    def ajax(self, request):
        form = self.form_class(data=json.loads(request.body))

        if form.is_valid():
            product_question = form.save(commit=False)
            product_question.user = self.request.user
            product_question.product = self.get_object()
            product_question.save()
            email_to = get_current_site(request).info.email
            form_email = form.cleaned_data['email']
            self.send_email(form, form_email, email_to)

            response_data = {'msg': self.form_valid_message}
        else:
            response_data = {'errors': form.errors}

        return self.render_json_response(response_data)

    def send_email(self, form, form_email, email_to):
        send_mail(
            unicode(_('You received a letter from the site {}'.format(get_current_site(self.request).domain))),
            unicode(_(u'User name: {}.\nEmail: {}.\nQuestion: {}'.format(form.cleaned_data['name'], form_email, form.cleaned_data['question']))),
            form.cleaned_data['email'],
            [email_to],
            fail_silently=False
        )


class ReviewsView(edit.CreateView, list.MultipleObjectMixin):
    form_class = ReviewForm
    model = ProductReview
    paginate_by = 20
    template_name = 'catalogue/review_list.html'
    context_object_name = 'reviews'

    def get_form_kwargs(self):
        kwargs = super(ReviewsView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return super(ReviewsView, self).get_queryset().exclude(status=self.model.FOR_MODERATION)

    def dispatch(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(ReviewsView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.status == self.model.FOR_MODERATION:
            messages.success(self.request, _("Your review appear after moderation by the administrator"))
        else:
            messages.success(self.request, _("Thank you for reviewing."))

        return reverse_lazy('catalogue:list-reviews')

