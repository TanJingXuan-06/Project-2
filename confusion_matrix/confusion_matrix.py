import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report,f1_score, precision_score, recall_score
import seaborn as sns

csv_files = pd.read_csv("Project2/data/scenario_predictions.csv", header = None)
y_actual = csv_files.loc[:,0]
y_pred = csv_files.loc[:,1]

labels = ['C1010', 'C1030', 'C3010', 'C3030', 'E1010', 'E1030', 'E3010', 'E3030']

model_cm = confusion_matrix(y_actual,y_pred, labels = labels)
model_acc = accuracy_score(y_actual,y_pred)
model_f1 = f1_score(y_actual,y_pred, average = 'macro')
model_pcs = precision_score(y_actual,y_pred, average = 'macro')
model_rc = recall_score(y_actual,y_pred, average = 'macro')

plt.figure(figsize=(8, 8))
cm = sns.heatmap(model_cm, annot=True, cmap=sns.cubehelix_palette(as_cmap=True), fmt= 'g', linecolor='black', linewidth = 0.5, clip_on = False, square = True, 
            xticklabels=['C1010', 'C1030', 'C3010', 'C3030', 'E1010', 'E1030', 'E3010', 'E3030'], 
            yticklabels=['C1010', 'C1030', 'C3010', 'C3030', 'E1010', 'E1030', 'E3010', 'E3030'])

plt.xlabel('Predicted', fontsize = 12)
plt.ylabel('Actual', fontsize = 12)
plt.title('8 by 8 Confusion Matrix', fontsize = 15)
plt.show()

report_dict = classification_report(y_actual, y_pred, output_dict=True)
print(report_dict)

print("\nClassification Metrics:")
for i in range(len(labels)):
    precision = report_dict[labels[i]]['precision']
    recall = report_dict[labels[i]]['recall']
    f1 = report_dict[labels[i]]['f1-score']

    print(f"Precision for {labels[i]} : {precision:.4f}")
    print(f"Recall for {labels[i]} : {recall:.4f}")
    print(f"F1 Score for {labels[i]} : {f1:.4f}\n")

print(f"Overall Accuracy: {model_acc:.4f}")
print(f"Overall Precision: {model_pcs:.4f}")
print(f"Overall Recall: {model_rc:.4f}")
print(f"Overall F1 Score: {model_f1:.4f}")