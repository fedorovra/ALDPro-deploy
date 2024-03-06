from django.http import HttpResponse
import ansible_runner

def index(request):
    a = ansible_runner.run(private_data_dir="/home/localadmin/ald-servers-install", 
                           playbook="playbook.yaml", 
                           quiet=True)
    return HttpResponse(a.status)
