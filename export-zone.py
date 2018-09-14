#!/usr/bin/env python

from __future__ import print_function
import boto3
import sys

route53 = boto3.client('route53')

paginate_hosted_zones = route53.get_paginator('list_hosted_zones')
paginate_resource_record_sets = route53.get_paginator('list_resource_record_sets')

domains = [domain.lower().rstrip('.') for domain in sys.argv[1:]]

for zone_page in paginate_hosted_zones.paginate():
    for zone in zone_page['HostedZones']:
        if domains and not zone['Name'].lower().rstrip('.') in domains:
            continue

        for record_page in paginate_resource_record_sets.paginate(HostedZoneId = zone['Id']):
            for record in record_page['ResourceRecordSets']:
                if record.get('ResourceRecords'):
                    for target in record['ResourceRecords']:
                        print(record['Name'], record['TTL'], 'IN', record['Type'], target['Value'], sep = "\t")
                elif record.get('AliasTarget'):
                    print(record['Name'], 300, 'IN', record['Type'], record['AliasTarget']['DNSName'], '; ALIAS', sep = "\t")
                else:
                    raise Exception('Unknown record type: {}'.format(record))
