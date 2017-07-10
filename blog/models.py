# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.
@python_2_unicode_compatible
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="posts")
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True)
    body = models.TextField()
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="likes")

    def __str__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = u'post'
        verbose_name_plural = u'Posts'
