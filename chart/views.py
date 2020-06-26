from django.shortcuts import render
from .models import Passenger
from django.db.models import Count, Q, FloatField, Sum
import json
from django.http import JsonResponse


def home(request):
    return render(request, 'home.html')


def world_population(request):
    return render(request, 'world_population.html')


def ticket_class_view_1(request):  # 방법 1
  dataset = Passenger.objects \
      .values('ticket_class') \
      .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                not_survived_count=Count('ticket_class', filter=Q(survived=False)),
                rate=(((1.0 * Count('ticket_class', filter=Q(survived=True), output_field=FloatField())) \
                / (1.0 * Count('ticket_class', filter=(Q(survived=True) | Q(survived=False)), output_field=FloatField()))) * 100.0)) \
      .order_by('ticket_class')

  return render(request, 'ticket_class_1.html', {'dataset': dataset})


def ticket_class_view_2(request):  # 방법 2
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False)),
                  rate=(((1.0 * Count('ticket_class', filter=Q(survived=True), output_field=FloatField())) \
                         / (1.0 * Count('ticket_class', filter=(Q(survived=True) | Q(survived=False)),
                                        output_field=FloatField()))) * 100.0)) \
        .order_by('ticket_class')

    # 빈 리스트 4종 준비
    categories = list()  # for xAxis
    survived_series = list()  # for series named 'Survived'
    not_survived_series = list()    # for series named 'Not survived'
    rate_series = list()    # for series named 'Rate'

    # 리스트 4종에 형식화된 값을 등록
    for entry in dataset:
        categories.append('%s Class' % entry['ticket_class'])  # for xAxis
        survived_series.append(entry['survived_count'])  # for series named 'Survived'
        not_survived_series.append(entry['not_survived_count'])  # for series named 'Not survived'
        rate_series.append(entry['rate'])  # for series named 'Rate'

    # json.dumps() 함수로 리스트 4종을 JSON 데이터 형식으로 반환
    return render(request, 'ticket_class_2.html', {
        'categories': json.dumps(categories),
        'survived_series': json.dumps(survived_series),
        'not_survived_series': json.dumps(not_survived_series),
        'rate_series' : json.dumps(rate_series)
    })


def ticket_class_view_3(request): # 방법 3
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False)),
                  rate=(((1.0 * Count('ticket_class', filter=Q(survived=True), output_field=FloatField())) \
                         / (1.0 * Count('ticket_class', filter=(Q(survived=True) | Q(survived=False)),
                                        output_field=FloatField()))) * 100.0)) \
        .order_by('ticket_class')

    # 빈 리스트 4종 준비 (series 이름 뒤에 '_data' 추가)
    categories = list()  # for xAxis
    survived_series_data = list()  # for series named 'Survived'
    not_survived_series_data = list()  # for series named 'Not survived'
    rate_series_data = list()   # for series named 'Rate'

    # 리스트 4종에 형식화된 값을 등록
    for entry in dataset:
        categories.append('%s Class' % entry['ticket_class'])  # for xAxis
        survived_series_data.append(entry['survived_count'])  # for series named 'Survived'
        not_survived_series_data.append(entry['not_survived_count'])  # for series named 'Not survived'
        rate_series_data.append(entry['rate'])  # for series named 'Rate'


    survived_series = {
        'name': '생존',
        'type': 'column',
        #'yAxis': 1,
        'data': survived_series_data,
        'tooltip': {'valueSuffix': '명'},
        'color': 'green'
    }
    not_survived_series = {
        'name': '비생존',
        'type': 'column',
        #'yAxis': 1,
        'data': not_survived_series_data,
        'tooltip': {'valueSuffix': '명'},
        'color': 'red'
    }
    rate_series = {
        'name': '생존율',
        'type': 'spline',
        'data': rate_series_data,
        'tooltip': {'valueSuffix': '%'},
        'color': 'blue'
    }

    chart = {
        'chart': {'zoomType': 'xy'},
        'title': {'text': '좌석 등급에 따른 타이타닉 생존/비 생존 인원 및 생존율'},
        'xAxis': {'categories': categories},
        'tooltip': {'shared': 'true'},
        'legend': {'layout': 'vertical', 'align': 'left', 'x': 120, 'verticalAlign': 'top', 'y': 100, 'floating': 'true'},
        'series': [survived_series, not_survived_series, rate_series]
    }
    dump = json.dumps(chart)

    return render(request, 'ticket_class_3.html', {'chart': dump})


def json_example(request): # 접속 경로 'json-example/'에 대응하는 뷰
    return render(request, 'json_example.html')


def chart_data(request): # 접속 경로 'json-example/data/'에 대응하는 뷰
    dataset = Passenger.objects \
        .values('embarked') \
        .exclude(embarked='') \
        .annotate(total=Count('id')) \
        .order_by('-total')

    port_display_name = dict()
    for port_tuple in Passenger.PORT_CHOICES:
        port_display_name[port_tuple[0]] = port_tuple[1]

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Number of Titanic Passengers by Embarkation Port'},
        'series': [{
            'name': 'Embarkation Port',
            'data': list(map
                (lambda row: {'name': port_display_name[row['embarked']],
                              'y': row['total']}, dataset))
        }]
     }

    return JsonResponse(chart)


import pandas as pd
import pandas_highcharts
from pandas_highcharts.core import serialize

def covid19_view(request):
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv', parse_dates=['Date'])
    countries = ['Korea, South', 'Germany', 'Japan', 'United Kingdom', 'US', 'France']
    df = df[df['Country'].isin(countries)]

    # 확진자 수 합계 열
    df['Cases_cf'] = df[['Confirmed']].sum(axis=1)

    # 확진자 합계 pivot
    df_cf = df.pivot(index='Date', columns='Country', values='Cases_cf')
    # df_cf.reset_index() 사용하여 index 리셋
    covid_cf = df_cf.reset_index('Date')
    # covid_cf 인덱스와 columns를 새로 지정
    covid_cf.set_index(['Date'], inplace=True)
    covid_cf.columns = countries

    populations = {'Korea, South': 51269185, 'Germany': 83783942, 'Japan': 126476461, 'United Kingdom': 67886011,
                   'US': 331002651, 'France': 65273511}

    # 확진자 수 인구 대비 건수 계산
    percapita_cf = covid_cf.copy()
    for country in list(percapita_cf.columns):
        percapita_cf[country] = percapita_cf[country] / populations[country] * 100000


    chart = pandas_highcharts.core.serialize(percapita_cf, render_to='my-chart', title='COVID 19', output_type='json')

    return render(request, 'covid_19.html', {'chart':chart})

