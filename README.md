# EBT Films Dose User Manual

## Purpose of the Program

The program is designed to process the results of radiochromic film dosimetry obtained from 16-bit per channel TIF scans and translate the image into a dose field. The program supports manual input of the calibration curve, a calibration database, various curve fitting modes, and outputs orthogonal projections of the final dose field to a text file.

## Main Interface Elements

- **Main Program Window**: Includes buttons for working with manual calibration, loading calibration from the database, and working with unirradiated film.
- **"DB and Settings" Window**: Displays the window for loading the calibration curve from the MongoDB database.
- **"Change Calibration List" Window**: Used for manual input of calibration files.
- **Dose Sections Viewing Window**: Displays the dose field on the right side of the main program window.

![Main Interface](https://i.ibb.co/k88KzJh/image.png)

*Main Interface*

## Example of Working with the Program

1. Select calibration parameters in "DB and Settings."
2. Visually check the calibration curve (optional).
3. Select unirradiated film and the film under study.
4. Set the DPI parameter and calculate the dose.
5. View orthogonal projections and output projection data.

## Description of Calibration Functions and Recommended Values

- **Optical Density Description Mode**: Includes various methods for describing optical density.
- **Curve Fitting Modes**: Includes various curve fitting methods.
- **Spline Fitting Modes**: Includes spline fitting methods.
- **Neural Network Fitting Modes**: Includes neural network fitting methods.

## Special Functions

- **Image Cropping**: Allows selecting an image area for cropping.
- **vmin/vmax Selection**: Changes the color palette for visual display.
- **Using Filters**: Includes various filters for image processing.
- **Saving to Excel**: Allows saving data in .xlsx format.
- **Shifting Axes of One-Dimensional Sections**: Allows shifting the function graph along the X-axis.
- **Calibration File Preparation**: Describes the process of preparing calibration files.
- **Statistics Output Window**: Displays statistical data on distributions in sections.

## Key Methods and Features

### Main Interface and Database Connection

- **Database Connection**: The program attempts to connect to the MongoDB database at startup.
- **Main Interface**: Includes various UI elements, such as buttons, layout widgets, and a toolbar for image manipulation.

### File Selection and Image Handling

- **Irradiated Film File Selection**: `get_irrad_film_file` method allows selecting and inserting an irradiated film file in TIFF format.
- **Empty Field File Selection**: `get_empty_field_file` method allows selecting and inserting an empty field file in TIFF format.
- **Image Insertion**: `insert_tiff_file` method inserts a picture of the film into the interface window.
- **Image Cropping**: `crop` and `cropping_by_button` methods allow cropping the image by selecting a specific area.

### Calculation Modes and Filters

- **Manual Calculation**: `calc_from_manual` method allows performing calculations manually.
- **Database Calculation**: `calc_from_db` method allows performing calculations using data from a connected database.
- **OD Only Calculation**: `calc_ODOnly` method sets z-data to a specific value for all data.
- **Filter Application**: `add_filter` method allows adding a filter to an image.

### Progress and Error Handling

- **Progress Bar**: `progress_bar_update` method updates the progress bar during calculations.
- **Error Handling**: Various warning messages inform the user about potential errors or issues.

### Application Window Configuration

- **Window Configuration**: The main application window is configured with a custom icon, title, and minimum size.

### Running the Program

The program can be run as a standalone application with the following code:

```python
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    application = CalcUI()
    application.setWindowTitle("Dose calculator")
    application.setMinimumSize(1200, 800)
    application.show()
    sys.exit(app.exec())

