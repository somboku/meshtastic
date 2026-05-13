from textual.app import App
from textual.widgets import Header, Footer, DataTable

class MeshUI(App):

    def compose(self):
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self):

        self.log(list(self.query("*")))
        print(list(self.query("*")))

app = MeshUI()
app.run(log="textual.log")


