from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
import ansible_runner

def index(request):
    if request.method == 'POST':
        with open("/home/localadmin/ALDPro-deploy/inventory/hosts", mode="w", encoding="utf-8") as out:
            out.write(render_to_string('hosts.j2', { "request" : request }))
        # a = ansible_runner.run(
        #     private_data_dir="/home/localadmin/ALDPro-deploy", 
        #     playbook="playbook.yaml", 
        #     quiet=True,
        # )
        # return render(request, 'finish.html', { 'status': a.status, })
        return render(request, 'finish.html', { 'status': "ok!", })
    return render(request, 'index.html', {})
