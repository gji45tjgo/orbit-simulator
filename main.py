from astropy import units as u
from poliastro.bodies import Earth, Mars, Sun, Moon, Venus, Mercury, Jupiter, Saturn, Uranus, Neptune
from poliastro.twobody import Orbit
from math import sqrt

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

tab1, tab2, tab3, tab4 = st.tabs(["Визуализация", "Окна связи", "Экспорт", "О проекте"])


st.sidebar.title("Настройки орбиты")
body = st.sidebar.selectbox("Планета", ["Земля", "Луна", "Марс", "Венера", "Меркурий", "Юпитер", "Сатурн", "Уран", "Нептун"], index=0)
apo = st.sidebar.number_input("Высота апогея (км)", value=2000)
per = st.sidebar.number_input("Высота перигея (км)", value=400)
inc = st.sidebar.slider("Наклонение (градусы)", min_value=0, max_value=180, value=60) * u.deg
num_points = st.sidebar.slider("Точек на орбите", min_value=50, max_value=20000, value=200, step=50)

bodies = {
    "Земля": Earth,
    "Луна": Moon,
    "Марс": Mars,
    "Венера": Venus,
    "Меркурий": Mercury,
    "Юпитер": Jupiter,
    "Сатурн": Saturn,
    "Уран": Uranus,
    "Нептун": Neptune
}

planet_colors = {
    "Земля": "Blues",
    "Луна": "gray",
    "Марс": "Reds",
    "Венера": [[0, 'ivory'], [1, 'goldenrod']],
    "Меркурий": "Greys",
    "Юпитер": [[0, 'beige'], [0.5, 'orange'], [1, 'brown']],
    "Сатурн": [[0, 'ivory'], [1, 'goldenrod']],
    "Уран": [[0, 'lightcyan'], [1, 'teal']],
    "Нептун": [[0, 'lightblue'], [1, 'darkblue']]
}

select_body = bodies[body]

st.set_page_config(page_title="Симулятор орбит", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

if per > apo:
    st.error("Перигей должен быть не выше апогея. Исправьте значения.")
    st.stop()
def calc_Orbit():

    r_apo = select_body.R + apo * u.km
    r_per = select_body.R + per * u.km

    a = (r_per + r_apo) / 2
    a_km = a.to(u.km).value
    ecc = (r_apo - r_per) / (r_apo + r_per)
    ecc_val = ecc.value


    nu_vals = np.linspace(0, 360, num_points) * u.deg

    orb_for_period = Orbit.from_classical(select_body, a, ecc, inc, 0 * u.deg, 0 * u.deg, 0 * u.deg)
    period = orb_for_period.period.to(u.min).value
    orb_perigee = orb_for_period.propagate_to_anomaly(0 * u.deg)
    orb_apogee = orb_for_period.propagate_to_anomaly(180 * u.deg)

    v_p_kms = np.linalg.norm(orb_perigee.v.to(u.km / u.s).value)
    v_a_kms = np.linalg.norm(orb_apogee.v.to(u.km / u.s).value)
    mu = select_body.k.to(u.km ** 3 / u.s ** 2).value
    v_circ = np.sqrt(mu / a_km)
    x_vals, y_vals, z_vals, velocity_list = [], [], [], []
    for nu in nu_vals:
        orb_nu = Orbit.from_classical(select_body, a, ecc, inc, 0 * u.deg, 0 * u.deg, nu)
        r = orb_nu.r
        x_vals.append(r[0].to(u.km).value)
        y_vals.append(r[1].to(u.km).value)
        z_vals.append(r[2].to(u.km).value)
        velocity_list.append(np.linalg.norm(orb_nu.v.to(u.km / u.s).value))
    return x_vals, y_vals, z_vals, period, ecc_val, a_km, v_a_kms, v_p_kms, v_circ, velocity_list

def calc_planet():
    dolg = np.linspace(0, 2 * np.pi, 40)
    shir = np.linspace(0, np.pi, 40)

    R_km = select_body.R.to(u.km).value
    x_planet = R_km * (np.outer(np.cos(dolg), np.sin(shir)))
    y_planet = R_km * (np.outer(np.sin(dolg), np.sin(shir)))
    z_planet = R_km * np.outer(np.ones(np.size(dolg)), np.cos(shir))

    return x_planet, y_planet, z_planet, dolg, shir

def export_data():
    df = pd.DataFrame({
        "X (км)": x_val,
        "Y (км)": y_val,
        "Z (км)": z_val,
        "Высота (км)": np.sqrt(np.array(x_val) ** 2 + np.array(y_val) ** 2 + np.array(z_val) ** 2) - select_body.R.to(
            u.km).value,
        "Скорость (км/с)": velocity_orb,
        "Время (мин)": time_orb,
        "Угол места (градусы)": elevation,
        "Видимость": visible,
        "Наклонная дальность (км)": v_d


    })
    df_export = df[columns_choice]
    csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')
    return csv_data

def calc_coordinat():
    lon_rad = np.radians(lon)
    lat_rad = np.radians(lat)
    theta = np.pi/2 - lat_rad
    R_km = select_body.R.to(u.km).value

    x_st = R_km * np.cos(lon_rad) * np.sin(theta)
    y_st = R_km * np.sin(lon_rad) * np.sin(theta)
    z_st = R_km * np.cos(theta)

    return x_st, y_st, z_st





x_val, y_val, z_val, period, ecc, a, v_a, v_p, v_c, velocity_orb = calc_Orbit()
x_planet, y_planet, z_planet, dold_arr, shir_arr = calc_planet()

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x_val, y=y_val, z=z_val,
        mode='lines',
        name='Орбита',
        line=dict(width=5, color='red' if select_body in [Earth, Neptune, Uranus] else 'blue')
    ))
    fig.add_trace(go.Surface(
        x=x_planet, y=y_planet, z=z_planet,
        colorscale=planet_colors[body],
        opacity=0.5,
        showscale=False
    ))

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            zaxis=dict(showticklabels=False)
        )
    )
    st.title("Симулятор орбит")
    st.plotly_chart(fig, use_container_width=True, height=700)


    st.subheader("Параметры орбиты")
    col1, col2, col3 = st.columns(3)
    col1.metric("Период", f"{period:.1f} мин")
    col2.metric("Большая полуось", f"{a:.0f} км")
    col3.metric("Эксцентриситет", f"{ecc:.4f}")

    st.subheader("Скорости")
    col4, col5, col6 = st.columns(3)
    col4.metric("Скорость в перигее", f"{v_p:.2f} км/с")
    col5.metric("Круговая", f"{v_c:.2f} км/с")
    col6.metric("Скорость в апогее", f"{v_a:.2f} км/с")


with tab2:
    st.markdown("""
    <style>
    div[data-testid="stPlotlyChart"] > div {
        border-radius: 20px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("Режим рассчета окн связи с КА")
    lon = st.number_input("Долгота (градусы)", min_value=-180.0, max_value=180.0, value=0.0, format="%.6f")
    lat = st.number_input("Широта (градусы)", min_value=-90.0, max_value=90.0, value=0.0, format="%.6f")
    min_elv = st.number_input("Минимальный угол места (градусы)", min_value=0.0, max_value=30.0, step=0.5, value=0.0)
    x_st, y_st, z_st = calc_coordinat()


    def calc_angle(min_elv):
        elevations = []
        visible = []
        time_orb = []
        v_list = []
        R = select_body.R.to(u.km).value
        for i in range(num_points):
            v_x = x_val[i] - x_st
            v_y = y_val[i] - y_st
            v_z = z_val[i] - z_st
            v = sqrt(v_x**2 + v_y**2 + v_z**2)
            v_list.append(v)

            up_x = x_st / R
            up_y = y_st / R
            up_z = z_st / R

            cos_alpha = (up_x*v_x + up_y*v_y + up_z*v_z) / v
            alpha_rad = np.arccos(cos_alpha)
            alpha_deg = np.degrees(alpha_rad)
            elv = 90.0 - alpha_deg
            elevations.append(elv)
            time_orb.append(period * i / num_points)
            visible.append(elv >= min_elv)

        return elevations, visible, v_list, time_orb

    def serch_winow():
        windows = []
        in_window = False
        start = None

        for index, val in enumerate(visible):
            if val == True and not in_window:
                start = index
                in_window = True
            elif val == False and in_window:
                end = index - 1
                time_start = period * start / num_points
                time_end = period * end / num_points
                max_el = max(elevation[start:end + 1])
                windows.append((time_start, time_end, max_el))
                in_window = False


        if in_window:
            end = num_points - 1
            time_start = period * start / num_points
            time_end = period * end / num_points
            max_el = max(elevation[start:end + 1])
            windows.append((time_start, time_end, max_el))
        colors = ['green' if v else 'red' for v in visible]

        if len(windows) >= 2 and visible[0] and visible[-1]:
            t_start = windows[-1][0] - period
            t_end = windows[0][1]
            max_el = max(windows[0][2], windows[-1][2])
            windows = windows[1:-1]
            windows.insert(0, (t_start, t_end, max_el))

        return colors, windows


    def import_trace():
        lon_list = []
        lat_list = []
        for i in range(num_points):
            r = sqrt(x_val[i] ** 2 + y_val[i] ** 2 + z_val[i] ** 2)
            lat = np.degrees(np.arcsin(z_val[i] / r))
            lon = np.degrees(np.arctan2(y_val[i], x_val[i]))
            lat_list.append(lat)
            lon_list.append(lon)
        return lat_list, lon_list


    def split_segments(lon_list, lat_list, colors):
        segments = []
        current_lon = [lon_list[0]]
        current_lat = [lat_list[0]]
        current_color = colors[0]

        for i in range(1, len(lon_list)):
            lon_diff = abs(lon_list[i] - lon_list[i - 1])

            if lon_diff > 180 or colors[i] != current_color:
                segments.append((current_lon, current_lat, current_color))
                current_lon = [lon_list[i]]
                current_lat = [lat_list[i]]
                current_color = colors[i]
            else:
                current_lon.append(lon_list[i])
                current_lat.append(lat_list[i])

        segments.append((current_lon, current_lat, current_color))
        return segments

    sphere = go.Surface(
        x=x_planet, y=y_planet, z=z_planet,
        colorscale=planet_colors[body],
        showscale=False,
        hoverinfo='skip'
    )

    data = [sphere]

    for i in range(len(shir_arr)):
        line = go.Scatter3d(
            x=x_planet[i, :], y=y_planet[i, :], z=z_planet[i, :],
            mode='lines',
            line=dict(color='black', width=1),
            hoverinfo='skip',
            showlegend=False
        )
        data.append(line)

    for j in range(len(dold_arr)):
        line = go.Scatter3d(
            x=x_planet[:, j], y=y_planet[:, j], z=z_planet[:, j],
            mode='lines',
            line=dict(color='black', width=1),
            hoverinfo='skip',
            showlegend=False
        )
        data.append(line)
    fig = go.Figure(data=data)
    fig.add_trace(go.Scatter3d(
        x=[x_st], y=[y_st], z=[z_st],
        mode='markers',
        name='Станция',
        marker=dict(size=8, color='green', symbol='circle')
    ))
    elevation, visible, v_d, time_orb = calc_angle(min_elv)
    colors, windows = serch_winow()
    lat_st = lat
    lon_st = lon
    lat_orb, lon_orb = import_trace()
    segments = split_segments(lon_orb, lat_orb, colors)

    fig.add_trace(go.Scatter3d(
        x=x_val, y=y_val, z=z_val,
        mode='lines',
        name='Орбита',
        line=dict(width=5, color=colors)
    ))

    if body == "Земля":
        fig2d = go.Figure()

        for seg_lon, seg_lat, seg_color in segments:
            fig2d.add_trace(go.Scattermapbox(
                lat=seg_lat, lon=seg_lon,
                mode='lines',
                line=dict(width=3, color=seg_color),
                hoverinfo='none', showlegend=False
            ))

        fig2d.add_trace(go.Scattermapbox(
            lat=[lat_st], lon=[lon_st],
            mode='markers',
            marker=dict(size=15, color='green', symbol='circle'),
            name='Станция', text=['Станция'], hoverinfo='text'
        ))

        fig2d.update_layout(
            mapbox=dict(
                style='carto-darkmatter',
                center=dict(lat=np.mean(lat_orb), lon=np.mean(lon_orb)),
                zoom=0, bearing=0, pitch=0
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor='black', plot_bgcolor='black',
            showlegend=False,
            height=500
        )

    else:
        fig2d = go.Figure()

        for lat_line in range(-90, 91, 30):
            fig2d.add_trace(go.Scattergeo(
                lon=list(range(-180, 181, 5)),
                lat=[lat_line] * 73,
                mode='lines',
                line=dict(color='gray', width=0.5),
                hoverinfo='none', showlegend=False
            ))

        for lon_line in range(-180, 181, 30):
            fig2d.add_trace(go.Scattergeo(
                lon=[lon_line] * 37,
                lat=list(range(-90, 91, 5)),
                mode='lines',
                line=dict(color='gray', width=0.5),
                hoverinfo='none', showlegend=False
            ))

        for seg_lon, seg_lat, seg_color in segments:
            fig2d.add_trace(go.Scattergeo(
                lon=seg_lon, lat=seg_lat,
                mode='lines',
                line=dict(width=3, color=seg_color),
                hoverinfo='none', showlegend=False
            ))

        # Станция
        fig2d.add_trace(go.Scattergeo(
            lon=[lon_st], lat=[lat_st],
            mode='markers',
            marker=dict(size=12, color='green', symbol='circle'),
            name='Станция', text=['Станция'], hoverinfo='text'
        ))

        fig2d.update_layout(
            geo=dict(
                projection_type='equirectangular',
                showland=False,
                showocean=False,
                showcoastlines=False,
                showcountries=False,
                bgcolor='rgb(14, 17, 23)'
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor='rgb(14, 17, 23)',
            plot_bgcolor='rgb(14, 17, 23)',
            showlegend=False,
            height=500
        )
    col_3d, col_2d = st.columns(2)

    with col_3d:
        fig.update_layout(
            scene=dict(
                aspectmode='data',
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False),
                zaxis=dict(showticklabels=False)
            ),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True, height=500)

    with col_2d:
        st.plotly_chart(fig2d, use_container_width=True, height=500,
                        config={
                            'scrollZoom': True,
                            'displayModeBar': False,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['zoomIn', 'zoomOut', 'resetScale']
                        })

    st.subheader("Окна связи")
    if windows:
        for i, (t_st, t_en, max_el) in enumerate(windows, 1):
            if t_st < 0:
                t_st += period
                t_en += period
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"Окно {i}: Начало", f"{t_st:.1f} мин")
            col2.metric("Конец", f"{t_en:.1f} мин")
            col3.metric("Длительность", f"{t_en - t_st:.1f} мин")
            col4.metric("Макс. угол", f"{max_el:.1f}°")
    else:
        st.warning("Нет окон связи при заданных параметрах.")

with tab3:
    st.title("Экспорт данных орбиты")
    columns_choice = st.multiselect(
        "Выберите столбцы для экспорта:",
        ["X (км)", "Y (км)", "Z (км)", "Высота (км)", "Скорость (км/с)", "Время (мин)", "Угол места (градусы)", "Видимость", "Наклонная дальность (км)"],
        default=["X (км)", "Y (км)", "Z (км)", "Высота (км)"]
    )
    st.download_button(
        label="Скачать (CSV)",
        data=export_data().encode('utf-8-sig'),
        file_name="orbit_coordinates.csv",
        mime="text/csv"
    )

with tab4:
    st.title("О проекте")

    st.header("Орбитальный симулятор")
    st.markdown("Версия 1.0")

    st.markdown("""
    **Орбитальный симулятор** — это образовательный инструмент для студентов 
    аэрокосмических специальностей. Позволяет моделировать орбиты космических 
    аппаратов вокруг планет Солнечной системы, рассчитывать окна связи 
    с наземными станциями и экспортировать данные для курсовых работ.
    """)

    st.subheader("Возможности")
    st.markdown("""
    - 🛰️ 3D-визуализация орбит с координатной сеткой
    - 🌍 Выбор планеты (Земля, Луна, Марс и другие)
    - 📡 Расчёт окон связи с наземной станцией
    - 🗺️ 2D-карта с трассой орбиты
    - 📥 Экспорт данных в CSV
    """)

    st.subheader("Технологии")
    st.markdown("""
    - **Python** — язык разработки
    - **Streamlit** — веб-интерфейс
    - **Poliastro** — орбитальная механика
    - **Plotly** — 3D и 2D визуализация
    - **Astropy** — астрономические вычисления
    """)

    st.subheader("Автор")
    st.markdown("""
    **Шешуков Павел**  
    [GitHub](https://github.com/gji45tjgo/orbit-simulator)  
    [📧 Написать на почту](https://mail.yandex.ru/compose?to=pasha.pavel169@yandex.ru)
    """)

    st.subheader("Лицензия")
    st.markdown("MIT License © 2026 Павел")
