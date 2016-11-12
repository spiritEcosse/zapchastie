from oscar.apps.customer.views import AccountAuthView as CoreAccountAuthView
from django.core.urlresolvers import reverse, reverse_lazy


class AccountAuthView(CoreAccountAuthView):
    def get_login_success_url(self, form):
        redirect_url = form.cleaned_data['redirect_url']
        if redirect_url:
            return redirect_url

        # Redirect staff members to dashboard as that's the most likely place
        # they'll want to visit if they're logging in.
        if self.request.user.is_staff:
            return reverse('admin:index')

        return set
