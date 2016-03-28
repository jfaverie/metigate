from django.contrib.auth.models import User
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from snippets.models import Snippet, Document
from snippets.permissions import IsOwnerOrReadOnly
from snippets.forms import DocumentForm
from snippets.serializers import SnippetSerializer, UserSerializer
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse



class SnippetViewSet(viewsets.ModelViewSet):

    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=(renderers.StaticHTMLRenderer,))
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users in the system.
    As you can see, the collection of snippet instances owned by a user are
    serialized using a hyperlinked representation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('snippets.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'snippets/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
