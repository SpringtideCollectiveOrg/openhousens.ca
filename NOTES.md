* Uses Django 1.7c1 on Python 3.4.1
* Uses [Bootstrap](http://getbootstrap.com/) instead of [Foundation](http://foundation.zurb.com/)
* Deploys to Heroku

## SayIt

* [Forks](https://github.com/opennorth/openhousens.ca/issues/2) SayIt to add better Akoma Ntoso support
* Omits or replaces all SayIt views
* Omits the following apps:
  * `django.contrib.humanize`
  * `django_select2`
* Omits the following middleware:
  * `speeches.middleware.InstanceMiddleware`
