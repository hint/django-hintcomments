from django.template import loader
from django.http import HttpResponseBadRequest

class FormInvalidResponse(HttpResponseBadRequest):
    """ Response that sends form with errors as a response """

    def __init__(self, templates, form, extra_errors=[], dictonary=None, **kwargs): # todo rewrite to be more form specific
        print extra_errors
        httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
        kwargs.update({'dictionary':{'form':form,'extra_errors':extra_errors}})
        if dictonary:
            kwargs['dictionary'].update(dictonary)
        print kwargs
        super(FormInvalidResponse, self).__init__(loader.render_to_string(templates, **kwargs), **httpresponse_kwargs)