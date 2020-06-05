import os
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader, PrefixLoader, select_autoescape
from jinja2_markdown import MarkdownExtension
from datetime import datetime

# multi_loader = jinja2.ChoiceLoader([
#         app.jinja_loader,
#         jinja2.PrefixLoader({'govuk-jinja-components': jinja2.PackageLoader('govuk-jinja-components')})
#     ])
# app.jinja_loader = multi_loader

config = yaml.safe_load(open("%s/config.yaml" % os.getcwd()))

multi_loader = ChoiceLoader([
        FileSystemLoader(config['templatesDir']),
        PrefixLoader({'govuk-jinja-components': PackageLoader('govuk-jinja-components')})
    ])

env = Environment(
    loader=multi_loader,
    autoescape=select_autoescape(['html', 'xml']),
    extensions=['jinja2_markdown.MarkdownExtension'],
)

def get_config():
  return yaml.safe_load(open("%s/config.yaml" % os.getcwd()))

def csv_boolean(val):
  result = None
  if val == "yes":
    result  = True
  elif val == "no":
    result = False
  return result

def csv_string(val):
  result = None
  if val != "":
    result  = str.strip(str(val))
  return result

def csv_list(val):
  return str.strip(val).split(",")

def csv_int(val):
  try:
    return int(val)
  except ValueError:
    return None

def csv_date(val):
    try:
        return datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        return None

def render(output_path, template_path, **kwargs):
  template = env.get_template(template_path)
  file = open(output_path, 'w')
  file.write(template.render(config=config, **kwargs))
  file.close()

def create_file(output_path, content):
  file = open(output_path, 'w')
  file.write(content)
  file.close()

def create_directory(path):
  if os.path.exists(path):
    shutil.rmtree(path)
  os.makedirs(path)
