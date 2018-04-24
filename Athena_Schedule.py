#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import requests
import json
import datetime
import csv
from datetime import datetime, timedelta

creds = json.load(open('Athena_Creds.json'))['secret_key']


class AvailabilityAudit(object):

    def authenticate(self):
        creds = json.load(open('Athena_Creds.json'))['secret_key']
        auth_url = 'https://api.athenahealth.com/oauth/token'
        payload = 'grant_type=client_credentials'

        headers = {'authorization': creds,
                   'content-type': 'application/x-www-form-urlencoded',
                   'cache-control': 'no-cache'}

        auth_response = requests.post(auth_url, data=payload,
                headers=headers)
        return json.loads(auth_response.text)['access_token']

    def get_athena_records(
        self,
        PRACTICE_ID,
        PROVIDER_ID,
        DEPARTMENT_ID,
        ):

        req_url = \
            'https://api.athenahealth.com/v1/%d/appointments/open' \
            % PRACTICE_ID

        # 'mm/dd/yyyy'....

        querystring = {
            'departmentid': DEPARTMENT_ID,
            'enddate': str(((datetime.now() + timedelta(days=28)).date()).strftime('%m/%d/%Y')),
            'ignoreschedulablepermission': 'true',
            'limit': '5000',
            'providerid': PROVIDER_ID,
            'reasonid': '-1',
            'showfrozenslots': 'false',

            }

        headers = {'Authorization': 'Bearer' + ' ' \
                   + self.authenticate(), 'Cache-Control': 'no-cache'}
        schedule = requests.request('GET', req_url, headers=headers,
                                    params=querystring)

        # return json.loads(schedule.text)['appointments']
        #print schedule.text
        #print querystring
        athena_avail=[]
        with open('AthenaScheduleOutput.csv', 'w+') as athena_op_file:
            writer = csv.DictWriter(athena_op_file, fieldnames=[
                'date',
                'appointmentid',
                'departmentid',
                'appointmenttype',
                'providerid',
                'starttime',
                'duration',
                'appointmenttypeid',
                'reasonid',
                'patientappointmenttypename',
                ])
            writer.writeheader()
            
            for slot in json.loads(schedule.text)['appointments']:
                writer.writerow(slot)
        return schedule.status_code

    def get_zd_records(
        self,
        PROVIDER_ID,
        FACILITY_ID,
        PATIENTYPE,
        ):

        req_url = \
            'https://www.zocdoc.com/api/3/professionallocation/timeslots'

        headers = {'Cache-Control': 'no-cache'}

        querystring = {
            'professional_location_ids': PROVIDER_ID + '_' \
                + FACILITY_ID,
            'date': str(datetime.now().date()),
            'days_ahead': '28',
            'procedure_id': '75',
            'availability_time_filter': '',
            'is_new_patient': PATIENTYPE,
            'apikey': '',
            'carrier_id': '358',
            'directory_id': '-1',
            'plan_id': '2556',
            'widget': '',
            }
        #print querystring

        response = requests.get(url=req_url, headers=headers,
                                params=querystring)
        response_dict = json.loads(response.text)
        f = lambda x: ('New' if x == 'true' else 'Est')
        schedule = response_dict['data']['professional_locations'
                ][0]['timeslots']
        zocdoc_avail=[]
        with open('ZocdocScheduleOutput.csv', 'w+') as zd_op_file:
            writer = csv.writer(zd_op_file, delimiter=',')
            writer.writerow(['Date','StartTime','ZocdocProviderID','ZocdocLocationID','New/Est'])
            for slot in schedule:
                #print slot
                date_time = slot[u'start_time'].split('T')
                writer.writerow([date_time[0],date_time[1][:8], PROVIDER_ID,
                                FACILITY_ID, f(PATIENTYPE)])
        return response.status_code


c =AvailabilityAudit()
c.get_zd_records("198168","51285","true")
time.sleep(1)
c.get_athena_records(683,"1010","441")

			