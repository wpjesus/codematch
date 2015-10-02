from ietf.codematch import constants

from django.shortcuts import render

from django.template import RequestContext

from ietf.person.models import Person, Alias
from ietf.codematch.matches.models import ProjectContainer, CodingProject
from ietf.codematch.requests.models import CodeRequest

import debug

# ----------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------
def is_user_allowed(user, permission):
	""" Check if the user has permission """
	
	return True

def get_user(request):

	if request.user.is_authenticated():
		return Person.objects.get(user=request.user)
	else:
		return None
	
def get_menu_arguments(request, dict):
    
	user = get_user(request)
	
	if user != None:
		
		my_codings 			  = CodingProject.objects.filter( coder = user )
		my_own_projects 	  = ProjectContainer.objects.filter( owner = user )
		my_mentoring_projects = ProjectContainer.objects.filter( code_request__mentor = user )
		
		# Some tests are made on the templates, should be here in the code?
		
		dict['from'] = request.GET.get('from', None)
		
		dict['codematch_version'] = constants.VERSION
		dict['codematch_revision_date'] = constants.RELEASE_DATE
		
		dict["mycodings"] 		  = my_codings
		dict["projectsowner"] 	  = my_own_projects
		dict["projectsmentoring"] = my_mentoring_projects
		
		dict["canaddcoding"] 	  = is_user_allowed(user, "canaddcoding")
		dict["canaddrequest"] 	  = is_user_allowed(user, "canaddrequest")
		dict["ismentor"] 	 	  = is_user_allowed(user, "ismentor")
		 
		# Try get pretty name user (otherwise, email will be used)
		alias = Alias.objects.filter( person = user )
		
		alias_name = alias[0].name if alias else user.name
		     
		dict["username"] = alias_name
        
	return dict

def clear_session(request):
	
	keys = [constants.ALL_PROJECTS, constants.PROJECT_INSTANCE, constants.REQUEST_INSTANCE, constants.ACTUAL_PROJECT, constants.CODE_INSTANCE, 
			constants.ADD_DOCS, constants.ADD_TAGS, constants.ADD_LINKS, constants.REM_DOCS, constants.REM_TAGS, constants.REM_LINKS]
	
	if constants.MAINTAIN_STATE not in request.session:
		for key in keys:
			if key in request.session:
				del request.session[key]
	else:
		del request.session[constants.MAINTAIN_STATE]

def render_page(request, template, dict = {}):
	""" Special method for rendering pages """
	
	clear_session(request)
	
	if constants.ACTUAL_TEMPLATE in request.session:
		actual_template = request.session[constants.ACTUAL_TEMPLATE]				
		if actual_template != request.path:
			request.session[constants.PREVIOUS_TEMPLATE] = actual_template
	
	request.session[constants.ACTUAL_TEMPLATE] = request.path
	
	return render(request, template, get_menu_arguments(request,dict))
