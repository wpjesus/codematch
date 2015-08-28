from django.shortcuts import render

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
   
def get_menu_arguments(request, dict):
    
	if request.user.is_authenticated():
		#(TODO: Centralize this?)
		user = Person.objects.get(user=request.user)
		
		my_codings 			  = CodingProject.objects.filter( coder = user )
		my_own_projects 	  = ProjectContainer.objects.filter( owner = user )
		my_mentoring_projects = ProjectContainer.objects.filter( code_request__mentor = user )
		
		dict["mycodings"] 		  = my_codings
		dict["projectsowner"] 	  = my_own_projects
		dict["projectsmentoring"] = my_mentoring_projects
		
		# TODO: add here others permissions (check how are used permissions)
		#TODO: Centralize the permissions and add the CRUD permissions
		dict["canaddrequest"] = is_user_allowed(user, "canaddrequest")
		dict["canaddcoding"]  = is_user_allowed(user, "canaddcoding")
		dict["ismentor"]      = is_user_allowed(user, "ismentor")
		 
		#Try get pretty name user (otherwise, email will be used)
		alias = Alias.objects.filter( person = user )
		 
		if alias:
		    alias_name = alias[0].name
		else:
		    alias_name = user.name
		     
		dict["username"] = alias_name
        
	return dict

def render_page(request, template, dict = {}):
	""" Special method for rendering pages """
	
	keys = ["project_instance", "request_instance", "docs", "tags"]
	
	if 'actual_template' in request.session:
		actual_template = request.session["actual_template"]
		if actual_template != template:
			for key in keys:
				if key in request.session:
					del request.session[key]
		
	request.session["actual_template"] = template
	
	return render(request, template, get_menu_arguments(request,dict))