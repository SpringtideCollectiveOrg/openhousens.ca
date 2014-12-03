* Uses Django 1.7 on Python 3.3.3
* Uses [Bootstrap](http://getbootstrap.com/) instead of [Foundation](http://foundation.zurb.com/)
* Deploys to Heroku

## SayIt

* Omits or replaces all SayIt views
* Replaces `SpeechIndex` and `SpeechForm`
* Omits the following apps:
  * `django.contrib.humanize`
  * `django_select2`
* Omits the following middleware:
  * `speeches.middleware.InstanceMiddleware`
