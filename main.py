from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.text import LabelBase

import pyvista as pv
import multiprocessing
import os

Builder.load_file('layout.kv')
plotter = pv.Plotter()
hidden_plotter = pv.Plotter(off_screen=True)

LabelBase.register(name='Faculty', fn_regular=r'FacultyGlyphic-Regular.ttf')

class MyLayout(Widget):
    mesh_volume_text = StringProperty()
    fat_percentage_text = StringProperty()
    img_src = StringProperty()

    user_name = None
    user_age = None
    user_height = 0
    user_weight = 0
    user_sex = None

    mesh = None
    mesh_volume = None

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        self.mesh_volume_text = 'Volume Sensor: ***'
        self.fat_percentage_text = 'Percentual de Gordura: ***'

    def update_name(self, name):
        self.user_name = name

    def update_age(self, age):
        self.user_age = int(age)

    def update_height(self, height):
        self.user_height = int(height if height is not '' else 0)

    def update_weight(self, weight):
        self.user_weight = int(weight if weight is not '' else 0)

    def calculate_fat_percentage(self, mesh_volume):
        lung_volume = (0.0472 * self.user_height + 0.000009 * self.user_weight - 5.92) * 1000
        liquid_volume = mesh_volume - lung_volume
        density = self.user_weight / liquid_volume
        fat_percentage = (437 / density) - 393
        return fat_percentage

    def choose_mesh(self):
        def cancel():
            popup.dismiss()

        def load(file_path):
            self.mesh = pv.read(file_path)
            self.mesh_volume = self.mesh.volume / 1000
            pool = multiprocessing.Pool()
            pool.apply_async(screenshot, [self.mesh]).get()
            self.img_src = 'mesh.png'
            self.mesh_volume_text = f'Volume Sensor: {self.mesh_volume:.2f}'

            popup.dismiss()

        content = FileSelector(load=load, cancel=cancel, execution_path=os.getcwd(), chosen_file_path='')
        popup = Popup(title='Selecione o arquivo', content=content)
        popup.open()

    def open_mesh(self):
        if self.mesh is None:
            return
        pool = multiprocessing.Pool()
        pool.apply_async(show, [self.mesh]).get()

    def get_results(self):
        if self.mesh is None or self.user_height is 0 or self.user_weight is 0:
            return
        fat_percentage = self.calculate_fat_percentage(self.mesh_volume)
        self.fat_percentage_text = f'Percentual de Gordura: {fat_percentage:.2f}%'

    def open_file_selector(self):
        self.ids.file_selector.text.open()

    pass


def show(mesh):
    plotter.add_mesh(mesh)
    plotter.show()


def screenshot(mesh):
    hidden_plotter.add_mesh(mesh)
    hidden_plotter.screenshot('mesh.png')


class FileSelector(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    execution_path = StringProperty()
    chosen_file_path = StringProperty()


Factory.register('FileSelector', cls=FileSelector)


class App(App):
    def build(self):
        return MyLayout()


if __name__ == '__main__':
    App().run()
