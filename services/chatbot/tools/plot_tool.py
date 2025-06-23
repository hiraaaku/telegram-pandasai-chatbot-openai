import plotly.express as px
import pandas as pd

from utils.table_description import table_description
from .sql_tool import ask_database

def plot_bar_line_area_chart(args):
    data = ask_database(args["query"])
    if isinstance(data, str):
        return data
    else:
        df = pd.DataFrame(data)
    if 'Bulan' in df.columns:
        df['Bulan'] = pd.to_datetime(df['Bulan'], format='%m').dt.strftime('%b')
    chart_type = args["chart_type"]
    del args["chart_type"]
    del args["query"]
    try:
        if chart_type == "bar":
            fig = px.bar(df, **args)
        elif chart_type == "area":
            fig = px.area(df, **args)
        elif chart_type == "line":
            fig = px.line(df, **args)
        elif chart_type == "histogram":
            fig = px.histogram(df, **args)
        else:
            return "Pembuatan plot gagal"
    except:
        return "Pembuatan plot gagal"
    fig.write_image("temp_chart.jpg")
    return "success"

def plot_pie_chart(args):
    data = ask_database(args["query"])
    if isinstance(data, str):
        return data
    else:
        df = pd.DataFrame(data)
    if 'Bulan' in df.columns:
        df['Bulan'] = pd.to_datetime(df['Bulan'], format='%m').dt.strftime('%b')
    del args["query"]
    try:
        fig = px.pie(df, **args)
    except:
        return "Pembuatan plot gagal"
    fig.write_image("temp_chart.jpg")
    return "success"

plot_bar_line_area_chart_function = {
     "type": "function",
     "name": "plot_bar_line_area_chart",
    "description": f"Gunakan fungsi ini untuk membuat bar chart, line chart, histogram chart, atau area chart menggunakan plotly. Berikut informasi mengenai tabel yang tersedia:\n\n{table_description}",
     "parameters": {
         "type": "object",
         "properties": {
            "query": {
                 "type": "string",
                 "description": "query untuk mengambil data",
             },
            "chart_type": {
                    "type": "string",
                    "enum": ["bar", "line", "chart", "histogram"],
                    "description": "tipe chart yang diinginkan"
            },
            "x": {
                "description": "kolom atau data-data untuk x axis",
                "type": "string"
            },
            "y": {
                "description": "kolom atau data-data untuk y axis",
                "oneOf": [
                    {
                        "type": "string"
                    },
                    {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                ]
            },
            "color" : {
                "type": "string",
                "description": "kolom dalam data yang digunakan untuk memberi warna berbeda pada tiap kategori"
            },
            "title": {
                "type": "string",
                "description": "judul chart"
            },
            "barmode": {
                "type": "string",
                "enum": ["group", "stack", "overlay", "relative"],
                "description": "mode chart bila chart_type yang dipilih adalah bar chart atau histogram chart"
            }
         },
         "required": ["query","chart_type","x","y", "title"]
     },
}

plot_pie_chart_function = {
     "type": "function",
     "name": "plot_pie_chart",
     "description": f"Gunakan fungsi ini untuk membuat pie chart menggunakan plotly. Berikut informasi mengenai tabel yang tersedia:\n\n{table_description}",
     "parameters": {
         "type": "object",
         "properties": {
            "query": {
                 "type": "string",
                 "description": "query untuk mengambil data",
             },
            "values": {
                "description": "kolom untuk value pada pie chart",
                "type": "string"
            },
            "names": {
                "description": "kolom untuk names untuk pie chart",
                "type": "string"
            },
            "color" : {
                "type": "string",
                "description": "kolom dalam data yang digunakan untuk memberi warna berbeda pada tiap kategori"
            },
            "title": {
                "type": "string",
                "description": "judul chart"
            },
         },
         "required": ["query","values","names","title"]
     },
}
