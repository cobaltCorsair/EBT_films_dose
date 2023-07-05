from DosesAndPaths import DosesAndPaths
import matplotlib
import numpy as np

application = None


class GraphicsPlotting:
    @staticmethod
    def draw_dose_map(z):
        """
        This method draws a map of dose distribution
        """
        application.figure_map.clf()
        ax = application.figure_map.add_subplot(111)
        application.cursor = matplotlib.widgets.Cursor(ax, useblit=False, color='red', linewidth=1)
        application.canvas_map.mpl_connect('button_press_event', lambda event: application.onclick(event, ax))
        application.canvas_map.draw()

        if DosesAndPaths.vmax is not None and DosesAndPaths.vmin is not None:
            im3 = ax.imshow(z, cmap="jet", vmin=DosesAndPaths.vmin, vmax=DosesAndPaths.vmax)
        else:
            im3 = ax.imshow(z, cmap="jet")

        formatter = lambda x, pos: round(x * DosesAndPaths.basis_formatter, 0)  # the resolution
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        application.figure_map.colorbar(im3, ax=ax, orientation="vertical")
        application.canvas_map.draw()

    @staticmethod
    def draw_curve(func, calculation_doses, setting_doses, p_opt, figure_graph, canvas_graph, sigma):
        """
        This method draws dose curve
        """
        figure_graph.clf()
        ax = figure_graph.add_subplot(111)
        ax.errorbar(calculation_doses, setting_doses, yerr=np.array(setting_doses[0:]) * (sigma / 100), fmt='ro',
                    label="Data points", markersize=6, capsize=5)
        ax.plot(calculation_doses, func(calculation_doses, *p_opt), label="Fit function", color="black", linestyle="-.")
        ax.grid(True, linestyle="-.")
        ax.legend(loc="best")
        ax.set_ylabel('Absorbed dose, Gy')
        ax.set_xlabel('Relative optical density')
        ax.set_xlim(0, np.max(calculation_doses) + 0.015)
        ax.set_ylim(0, np.max(setting_doses) + 0.5)
        canvas_graph.draw()

    @staticmethod
    def draw_curve_from_db(doses, ods, dose_object, figure_graph, canvas_graph):
        figure_graph.clf()
        ax = figure_graph.add_subplot(111)
        ax.plot(ods, doses, '*', label="Data points", color="red")
        ax.plot(np.linspace(ods[0], ods[-1], 500), dose_object.evaluateOD(np.linspace(ods[0], ods[-1], 500)),
                label="Fit function", color="black")
        ax.grid(True, linestyle="-.")
        ax.legend(loc="best")
        ax.set_ylabel('Absorbed dose, Gy')
        ax.set_xlabel('Relative optical density')
        canvas_graph.draw()