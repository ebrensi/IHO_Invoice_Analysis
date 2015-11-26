#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the analysis script for the IHO venue pricing project

"""

import pandas as pd
NaN = pd.np.nan


# This is a little function to output an easier-to-read csv file
#  for a multi-indexed DataFrame.  It eliminates duplicated index entries
#  along index columns.
# The csv file produced is meant to be used for viewing by humans.
def to_nice_csv(df, filename):
    x = df.reset_index()
    cols = df.index.names
    mask = (x[cols] == x[cols].shift())
    x.loc[:, cols] = x[cols].mask(mask, '')

    x.to_csv(filename, index=False, float_format='%5.2f')


# Read data into a dataframe
df = pd.read_csv('IHO_event_invoice_line_items.csv')
discounted = df['discount_type'] != 'NONE'
df.loc[discounted, 'discount_type'] = 'DISCOUNT'
df.loc[~discounted, 'discount_type'] = 'NO_DISCOUNT'

# Line items for only rooms, not including other associated invoice items
df_rooms_only = (df.query('item_type == "ROOM"')
                 .drop(['item_type'], axis=1)
                 .rename(columns={'item': 'room'}))


# We'll specify only certain rooms to simplify the output for now
# selected_rooms = ['BROADWAY']
# df_rooms_only = df_rooms_only[df_rooms_only['item'].isin(selected_rooms)]


grouped_by_room = (df_rooms_only
                   .groupby(['room', 'membership', 'discount_type']))

room_counts = grouped_by_room['room'].count()
room_counts.name = 'count'

# Output Room rental summaries
room_sums = grouped_by_room['HOURS_UNITS', 'SUBTOTAL', 'TOTAL'].sum()

room_sums['EFF_RATE'] = (room_sums['TOTAL'] /
                         room_sums['HOURS_UNITS'])

to_nice_csv(pd.concat([room_sums, room_counts], axis=1),
            'IHO_pricing_rooms_only_sum.csv')

room_means = grouped_by_room['AMOUNT',
                             'HOURS_UNITS',
                             'SUBTOTAL',
                             'DISCOUNT',
                             'TOTAL'].mean()
room_means['EFF_RATE'] = (room_means['TOTAL'] /
                          room_means['HOURS_UNITS'])


to_nice_csv(pd.concat([room_means, room_counts], axis=1),
            'IHO_pricing_rooms_only_avg.csv')


to_nice_csv(room_means[["AMOUNT", "EFF_RATE"]],
            'IHO_pricing_effective_room_rates.csv')


"""
# Try an alternative method of aggregation
table = pd.pivot_table(df_rooms_only,
                       index=['item', 'day_type',
                              'membership', 'discount_type'],
                       values=['SUBTOTAL', 'TOTAL'],
                       aggfunc=[pd.np.sum, pd.np.mean,
                                lambda x: len(x.unique())], fill_value=0)

to_nice_csv(table, 'IHO_pricing_rooms_only_pivot.csv')
"""

# Now do the same thing for services
df_services_only = (df.query('item_type == "SERVICE"')
                    .drop(['item_type'], axis=1)
                    .rename(columns={'item': 'service'}))

grouped_by_service = (df_services_only
                      .groupby(['service', 'membership', 'discount_type']))

table = pd.pivot_table(df_services_only,
                       index=['service', 'day_type',
                              'membership', 'discount_type'],
                       values=['SUBTOTAL', 'TOTAL'],
                       aggfunc=[pd.np.sum, pd.np.mean], fill_value=0)

to_nice_csv(table, 'IHO_pricing_services_only.csv')
