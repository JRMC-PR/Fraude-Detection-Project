# Fraud Detection in Banking System

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Data](#data)
- [Model Description](#model-description)
- [Evaluation Metrics](#evaluation-metrics)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)



## Introduction
Fraud detection in banking is crucial for protecting customer assets and maintaining the trustworthiness of financial institutions. This project leverages machine learning techniques to identify potentially fraudulent transactions.



## Features
- Creater user history using machine learning
- Detect fraudulent activities susch as:
  - Modifications in accounts credentials
  - Multiple accounts triyin gto lig in from the same place
  - Brute froece changing numerical value of user name
  - Multiple log in attems in a short time frame



## Technologies Used
- **Programming Language**: Python
- **Libraries**: NumPy, Pandas, Scikit-learn, TensorFlow/Keras, Matplotlib
- **Database**:  SAS
- **Files**: CSV



## Installation
1. Clone the repository:
   ```bash
   git clone git@github.com:JRMC-PR/Fraude-Detection-Project.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Fraude-Detection-Project
   ```
3. Install dependencies:
   ```bash
   Python
   pip
   pyfiglet
   pandas
   numpy
   hmmlearn
   tensorflow
   hdbscan
   scikit-learn
   ```

## Usage
1. Download the data sets of the RSA and Costumer AUTH from SAS And placed them in the respecting folders:
   ```
   EX. Data/Raw_Data/RSA_DATA/Agosto_1_2024.csv
   Ex. Data/Raw_Data/AUTH_DATA/Agosto_1_2024.csv

   ```
2. Train the model:
   ```
   Run the main file located in the models folder in the
   projects working tree

   python3 main.py

   And enter the file names for ther RSA and AUTH data sets
   ```


## Data
The dataset includes information on financial transactions, including:
- **RSA**:
- **'USER_ID**
- **USER_NAME**
- **DATA_S_**
- **IP_ADDRESS**
- **IP_CITY**
- **TIMEZONE**
- **EVENT_TIME**
- **DATA_S_4**
- **DATA_S_34**
- **RISK_SCORE**
- **EVENT_TYPE**

- **AUTH**:
- **ID**
- **PROFILE_ID**
- **EVENT_DATE**
- **USERNAME**
- **EVENT**
- **IP**
- **SESSIONID**
- **SEVERITY**
- **SERVER**
- **TRACE**
- **REPORT_DATE**
- **LOAD_DATE**


*Note*: Ensure data privacy by anonymizing sensitive information and adhering to GDPR or other relevant regulations.



## Model Description
- **Algorithm**:
   - **Histopry model**: Hmm and LSTM
- **Brute Force**: HDBSCAN and Isolation Forest


## Results
    In conclusion, we where not able to complete the intere propject do to insufficent data analisys, multiple restrictions from the bank and the lack of time to complete the project. We where able to create a model that can detect multiple log in attemps in a short time frame and brute force attacks. multiple log in attemps in a short time frame and brute force attacks. multiple logins from the same Ip and a History model that builds a user history to detect anomalies in the user behavior.

    We are still missing the implementations of the Risk scoring model and fine tunning th eprev 2 models made


## Authors Information
This project was developed by;

- Juan R. Silva, a Data Scientist, Software Developer, Student at Holberton Coding School and much more!

   ### Contact
- **Email**: [juansilva.dvm@gmail.com](mailto:juansilva.dvm@gmail.com)
- **GitHub**: [github.com/Mizuinu30](https://github.com/Mizuinu30)

    In colaboration with:

    - Jesus R Mendez(Ipsum Lorem et)

    ### Contact
- **Email**: [your-email@example.com](mailto:your-email@example.com)
- **GitHub**: [github.com/JRMC-PR](https://github.com/JRMC-PR)



    - Hector J Vasquez (lor at  ipsum astra)

    ### Contact
- **Email**: [jjvazquez96@gmail.com](mailto:jjvazquez96@gmail.com)
- **GitHub**: [github.com/pepesaur96](https://github.com/pepesaur96)


    - Juan C Rodriguez(lores ipsum dolor sit amet)

    ### Contact
- **Email**: [Juancarlos-99@live.com](mailto:Juancarlos-99@live.com)
- **GitHub**: [github.com/JCRoooD](https://github.com/JCRoooD)

    - Guillermo Pereyo(lores ipsum)
    ### Contact
- **Email**: [gpereyo@gmail.com.com](mailto:gpereyo@gmail.com.com)
- **GitHub**: [github.com/GuilleP2018](https://github.com/GuilleP2018)


