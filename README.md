# Preliminar note

This is a forked version of tastypie-nonrel tuned to fit my needs (and actually to
make it work). Use it at your own risk, to be honest I'm very far away from understanding
what is really going on down there.

I'm not interested in maintening it so if this is your desire don't hesitate to tell it to
me. On the other hand I will happyly accept pull requests.

# Introduction

This is an extension of [django-tastypie](https://github.com/toastdriven/django-tastypie/)
to support [django-nonrel](http://www.allbuttonspressed.com/projects/django-nonrel)
the fork of django with nonrelational backends, and MongoDB in particular. 

It should proof useful when Django 1.4 incorporates non-relational backends. 

Still under development.

# Usage

Similar to [djangtastypie](https://github.com/toastdriven/django-tastypie/) but instead
of use ModelRessource use MongoRessource that you have to import from
*tastypie_nonrel.ressources* instead of *tastypie.ressources*.

# Running tests

In order to run the tests, you should:

Get mongod running in your localhost.

Download the latest version from here:

http://www.mongodb.org/downloads

Instructions to install it in mac os x can be found here:

http://shiftcommathree.com/articles/how-to-install-mongodb-on-os-x

I would recommend using virtualenvwrapper:
http://www.doughellmann.com/projects/virtualenvwrapper/

## Create a new environment, like so if you set up virtualenvwrapper

  mkvirtualenv --no-site-packages django-tastypie-nonrel

## Or create one right here and get in it

  virtualenv --no-site-packages django_tastypie_nonrel-env
  source django_tastypie_nonrel-env/bin/activate

## Install reqs

  pip install -r requirements.txt

## Run tests

  python manage.py test eg

Not very surprisingly, most of the fields were easily repurposed for
non-relational fields. List and Dict fields are working fine, it seems.

Embedded fields reuse ToOneField. They are working except for update 
operations. This is because in # order to update, django-mongodb-engine 
uses A queries:
http://django-mongodb-engine.github.com/mongodb-engine/embedded-objects.html#updating

ListFields of EmbeddedFields use ToManyField and work for read, and almost for
write

// This software was written listening to Ratatat. You might like them.
