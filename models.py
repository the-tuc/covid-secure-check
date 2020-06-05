import os
import yaml
import json
import validators
from slugify import slugify
from urllib.parse import urlparse

class RiskAssessment:

  _validation_errors = []

  employer = None
  employer_website_url = None
  employer_address = None
  workplace = None
  employer_website_url = None
  employer_address = None
  approximate_number_of_workers = None
  public_visit = None
  risk_assessment_status = None
  risk_assessment_url = None
  risk_assessment_title = None
  risk_assessment_date = None
  additional_information_url = None
  union_presence = None
  sic_codes = []
  company_number = None

  def to_json(self):

    data = {
              "employer": self.employer,
              "employer_website_url": self.employer_website_url,
              "emplyer_address": self.employer_address,
              "workplace": self.workplace,
              "workplace_website_url": self.workplace_website_url,
              "workplace_address": self.workplace_address,
              "workplace_approximate_number_of_workers": self.workplace_approximate_number_of_workers,
              "public_visit": self.public_visit,
              "risk_assessment_status": self.risk_assessment_status,
              "risk_assessment_url": self.risk_assessment_url,
              "risk_assessment_title": self.risk_assessment_title,
              "risk_assessment_date": self.risk_assessment_date.strftime("%Y-%m-%d") if self.risk_assessment_date else None,
              "additional_information_url": self.additional_information_url,
              "union_presence": self.union_presence,
              "sic_codes": self.sic_codes,
              "company_number": self.company_number,
              }
    return json.dumps(data)

  def get_slug(self):
      return slugify("%s %s" % (self.employer, self.workplace))

  def get_risk_assessment_domain(self):
    return urlparse(self.risk_assessment_url).netloc

  def is_valid(self):
    self._validation_errors = []
    if self.employer is None:
      self._validation_errors.append("Employer is a required field")
    if not self.employer_website_url == None and not validators.url(self.employer_website_url):
      self._validation_errors.append("Employer website url must be a url or None")
    if self.workplace is None:
      self._validation_errors.append("Workplace is a required field")
    if not self.workplace_website_url == None and not validators.url(self.workplace_website_url):
      self._validation_errors.append("Workplace website url must be a url or None")
    if not type(self.workplace_approximate_number_of_workers) is int and not self.workplace_approximate_number_of_workers is None:
      self._validation_errors.append("Number of workers must be a string or None")
    if not self.public_visit in (True, False, None):
      self._validation_errors.append("Public visit must be True, False or None")
    if not self.risk_assessment_status in ("public", "private", "on request") and not self.risk_assessment_status is None:
      self._validation_errors.append("risk assessment published must be public, private or None")
    if not self.risk_assessment_url == None and not validators.url(self.risk_assessment_url):
      self._validation_errors.append("assessment URL must be a url or None")
    if not type(self.risk_assessment_title) is str and not self.risk_assessment_title is None:
      self._validation_errors.append("Risk assessment title must be an string or None")
    if not self.additional_information_url == None and not validators.url(self.additional_information_url):
      self._validation_errors.append("additional information URL must be a url or None")
    if not self.union_presence in (True, False, None):
      self._validation_errors.append("Union presence must be True, False or None")
    if not type(self.sic_codes) is list:
      self._validation_errors.append("Sic codes must be a list")

    return self._validation_errors == []
