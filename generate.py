import os
import shutil
import glob
import yaml
import csv
import sass
import requests
import models
from jinja2 import Template
from helpers import get_config, render, create_directory, create_file, csv_boolean, csv_list, csv_string, csv_int, csv_date
import frontmatter
from mailchimp3 import MailChimp
from shutil import copyfile

config = get_config()

# Download data from Google docs etc
response = requests.get(config['riskAssessmentCsvUrl'])
risk_assessments_file = open('%s/risk-assessments.csv' % config['dataDir'], 'w')
risk_assessments_file.write(response.text)
risk_assessments_file.close()

# Load risk assessments from CSV
risk_assessments = []
with open('%s/risk-assessments.csv' % config['dataDir']) as csv_file:
  assessments_csv = csv.DictReader(csv_file)
  for item in assessments_csv:
      risk_assessment = models.RiskAssessment()
      risk_assessment.employer = csv_string(item['employer'])
      risk_assessment.employer_address = csv_string(item['employer address'])
      risk_assessment.employer_website_url = csv_string(item['employer website url'])
      risk_assessment.workplace = csv_string(item['workplace'])
      risk_assessment.workplace_address = csv_string(item['workplace address'])
      risk_assessment.workplace_website_url = csv_string(item['workplace website url'])
      risk_assessment.workplace_approximate_number_of_workers = csv_int(item['workplace approximate number of workers'])
      risk_assessment.risk_assessment_status = csv_string(item['risk assessment status'])
      risk_assessment.risk_assessment_url = csv_string(item['risk assessment url'])
      risk_assessment.risk_assessment_title = csv_string(item['risk assessment title'])
      risk_assessment.risk_assessment_date = csv_date(item['risk assessment date'])
      risk_assessment.additional_information_url = csv_string(item['additional information url'])
      risk_assessment.public_visit = csv_boolean(item['public visit'])
      risk_assessment.union_presence = csv_boolean(item['union presence'])
      risk_assessment.sic_codes = csv_list(item['sic codes'])
      risk_assessment.company_number = csv_int(item['company number'])
      if risk_assessment.is_valid():
        risk_assessments.append(risk_assessment)
      else:
        print("Invalid risk assessment  %s" % ", ".join(risk_assessment._validation_errors))

# mailchimp
mailchimp_api_key = os.environ['MAILCHIMP_API_KEY']
mailchimp_username = os.environ['MAILCHIMP_USERNAME']
mailchimp_audience_id = os.environ['MAILCHIMP_AUDIENCE_ID']
mailchimp_client = MailChimp(mc_api=mailchimp_api_key, mc_user=mailchimp_username)
mailchimp_list = mailchimp_client.lists.get(mailchimp_audience_id)

# Stats
stats = {'risk_assessments': 0, 'volunteers': 0, 'risk_assessments_public': 0, 'risk_assessments_private': 0, 'risk_assessments_onrequest': 0, 'risk_assessments_unknown': 0}
stats['risk_assessments'] = len(risk_assessments)
stats['volunteers'] = mailchimp_list['stats']['member_count']

# output directory
create_directory(config['outputDir'])

create_directory("%s/assets" % config['outputDir'])

# Risk assessments
create_directory("%s/risk-assessments" % config['outputDir'])
for risk_assessment in risk_assessments:

  if risk_assessment.risk_assessment_status == 'public':
    stats['risk_assessments_public'] += 1
  elif risk_assessment.risk_assessment_status == 'private':
    stats['risk_assessments_private'] += 1
  elif risk_assessment.risk_assessment_status == 'on request':
    stats['risk_assessments_onrequest'] += 1
  elif risk_assessment.risk_assessment_status == None:
    stats['risk_assessments_unknown'] += 1

  #html
  render("%s/risk-assessments/%s.html" % (config['outputDir'], risk_assessment.get_slug()), "risk-assessment.html", risk_assessment=risk_assessment)

  # #json
  # create_file("%s/risk-assessments/%s.json" % (config['outputDir'], risk_assessment.get_slug()), risk_assessment.to_json())

# Risk assessment index
render("%s/%s" % (config['outputDir'], "risk-assessments/index.html"), "risk-assessments.html", risk_assessments=risk_assessments, stats=stats)

# index page
render("%s/index.html" % config['outputDir'], "index.html", stats=stats)

# volunteers
create_directory("%s/monitors" % config['outputDir'])
render("%s/monitors/index.html" % config['outputDir'], "volunteer.html")
render("%s/monitors/check-email.html" % config['outputDir'], "volunteer-check-email.html")
render("%s/monitors/confirmed.html" % config['outputDir'], "volunteer-confirmed.html")

# Report
render("%s/report.html" % config['outputDir'], "report.html")

# static pages
for path in glob.glob('%s/static/*.md' % config['dataDir']):
  page = frontmatter.load(path)
  #replaces any config variables in markdown
  parsed_content = Template(page.content)
  page.content = parsed_content.render(config=get_config())
  file_name = os.path.basename(path).replace('.md', '.html')
  render("%s/%s" % (config['outputDir'], file_name), "static.html", page=page)

# reports and guides
create_directory("%s/reports" % config['outputDir'])
for path in glob.glob('%s/reports/*.md' % config['dataDir']):
  page = frontmatter.load(path)
  #replaces any config variables in markdown
  parsed_content = Template(page.content)
  page.content = parsed_content.render(config=get_config())
  file_name = os.path.basename(path).replace('.md', '.html')
  render("%s/reports/%s" % (config['outputDir'], file_name), "static.html", page=page)


#assets
path = "assets/CNAME"
file_name = os.path.basename(path)
copyfile(path, "%s/CNAME" % config['outputDir'])

for path in glob.glob('%s/*.js' % config['assetsDir']):
  file_name = os.path.basename(path)
  copyfile(path, "%s/assets/%s" % (config['outputDir'], file_name))
  
for path in glob.glob('%s/*.png' % config['assetsDir']):
  file_name = os.path.basename(path)
  copyfile(path, "%s/assets/%s" % (config['outputDir'], file_name))

for path in glob.glob('%s/*.svg' % config['assetsDir']):
  file_name = os.path.basename(path)
  copyfile(path, "%s/assets/%s" % (config['outputDir'], file_name))

path = "node_modules/govuk-frontend/govuk/all.js"
file_name = os.path.basename(path)

copyfile(path, "%s/assets/govuk.js" % config['outputDir'])
sass.compile(dirname=('assets', 'docs/assets'), output_style='compressed')
