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
        else:
            return "Pembuatan plot gagal"
    except:
        return "Pembuatan plot gagal"
    fig.write_image("temp_chart.jpg")
    return "success"


plot_bar_line_area_chart_function = {
     "type": "function",
     "name": "plot_bar_line_area_chart",
    "description": f"Gunakan fungsi ini untuk membuat bar chart, line chart, atau area chartmenggunakan plotly. Berikut informasi mengenai tabel yang tersedia:\n\n{table_description}",
     "parameters": {
         "type": "object",
         "properties": {
            "query": {
                 "type": "string",
                 "description": "query untuk mengambil data",
             },
            "chart_type": {
                    "type": "string",
                    "enum": ["bar", "line", "chart"],
                    "description": "tipe chart yang diinginkan"
            },
            "x": {
                "type": "string",
                "description": "kolom untuk x axis"
            },
            "y": {
                "type": "string",
                "description": "kolom untuk y axis"
            },
            "color" : {
                "type": "string",
                "description": "kolom dalam data yang digunakan untuk memberi warna berbeda pada tiap kategori"
            },
            "title": {
                "type": "string",
                "description": "judul chart"
            },
            "bar_mode": {
                "type": "string",
                "enum": ["group", "stack", "overlay", "relative"],
                "description": "mode bar chart bila chart_type yang dipilih adalah bar chart"
            }
         },
         "required": ["query","chart_type","x","y"]
     },
}
