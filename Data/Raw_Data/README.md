# 📌 Data Storage Guidelines for Fraud Detection Model

## 📂 **Data Format**
- All data **must be in CSV format** (`.csv`).
- Ensure proper formatting and consistency before feeding data into the model.

---

## 📍 **Data Storage Location**
This is where the data will be stored and later fed into the fraud detection model.

### **🔹 General Rules**
- The **Raw_Data** folder contains subfolders for each month where the extracted data should be placed.
- Data extracted from different database tables should be stored in their respective folders.

---


## 📑 **Data Organization Rules**
### 🔹 **RSA Table Data**
- Should be placed inside the **`RSA_DATA`** folder.
- Store it in the correct month-based subfolder.
- Example:
  - Data extracted on **Agosto 2, 2024**, from the **RSA Table** should be placed in:
    ```
    Raw_Data/RSA_DATA/Agosto_2024/Agosto_2_2024.csv
    ```
## 📌 **Note:**
        The name of the file MUST FOLLOW THIS FORMAT:
        Month_Date_Year.csv
### **Example:**

  ### `Agosto_13_2024.csv`

### 🔹 **AUTH Table Data**
- Should be placed inside the **`AUTH_DATA`** folder.
- Store it in the correct month-based subfolder.
- Example:
  - Data extracted on **Diciembre 2, 2024**, from the **AUTH Table** should be placed in:
    ```
    Raw_Data/AUTH_DATA/Diciembre_2024/Diciembre_2_2024.csv
    ```
## 📌 **Note:**
        The name of the file MUST FOLLOW THIS FORMAT:
        Month_Date_Year.csv
### **Example:**

  ### `Diciembre_2_2024.csv`
---

## ⚠️ **Important Notes**
✔ Ensure the correct **file naming** and **folder placement**.
✔ The model **expects data in the designated folder structure**.
✔ Data from **different months must be stored separately** to maintain organization.
✔ Only **CSV files** are supported—any other format may cause errors in processing.

---

## 📞 **Need Help?**
If you have any issues or questions regarding data storage, please reach out to the team.

🚀 **Happy Data Processing!**
