import os
from deta import Deta

__all__ = (
    'Field',
    'Form',
    'Manager',
    )


def getenv(name):
    return os.environ.get(name) if name in os.environ else {i.strip().split('=')[0]:i.strip().split('=')[1] for i in open('.env').readlines()}[name]

class Field: # Not to be manually called. Called by Form class constructor
    def __init__(self,**kwargs):
        self.form_id = kwargs.get("form_id",None)
        self.type = kwargs.get("type",None)
        self.name = kwargs.get("name",None)
        self.required = kwargs.get("required",True)
        self.options = kwargs.get("options",[])

class Form:
    def __init__(self,**kwargs) -> None:
        self.form_id = kwargs.get("form_id",None)
        self.author = kwargs.get("author",None)
        self.name = kwargs.get("name",None)
        self.fields:list[Field] = []
        for index,item in enumerate(kwargs.get("fields",[])):
            self.fields.append(Field(**(vars(item)|{"form_id":self.form_id,"field_id":index})))

    def raw(self):
        data= {
            "author":self.author,
            "name":self.name,
            "fields":[vars(i) for i in self.fields]
        }
        if self.form_id is not None:
            data["form_id"] = self.form_id

        return data

class User:
    def __init__(self,google_id, form_ids):
        self.google_id = google_id
        self.form_ids:list[str] = form_ids #List of Form IDs
    
    def get_form(self,forms):
        return [i for i in forms if i.id in self.form_ids]

class Manager:
    def __init__(self):
        self.client = Deta(getenv('deta_api_key'))
        self.retrieve_users()
        self.retrieve_forms()

    def retrieve_users(self):
        self.users = User(self.client.Base('afoirm-users'))

    def get_user(self,google_id):
        return [i for i in self.users if i.id == google_id]

    def put_user(self, google_id, data):   
        return User(self.client.Base('afoirm-users').put(google_id, data))

    def retrieve_forms(self):
        self.forms = [Form(i.id,i.author,i.name,i.fields) for i in self.client.Base('afoirm-forms').fetch()['items']] #TO Change to Recurring fetch in future

    def get_form(self,form_id):
        return [i for i in self.forms if i.form_id == form_id]

    def delete_field(self, google_id, form_id, field_id):
        form = self.client.Base('afoirm-forms').get(form_id)
        fields = form.fields.pop(field_id)
        if int(field_id)+1 <= len(form.fields) and form.author==google_id:
            return self.client.Base('afoirm-forms').update(form_id,{"fields":fields})


