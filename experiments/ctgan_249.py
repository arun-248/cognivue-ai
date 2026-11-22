"""CTGAN augmentation experiment on the 249-response modelling data (research record; not used by the app).
Usage: python ctgan_249.py <folder with X.csv and y.csv> <epochs> [n_folds]
X.csv holds the nine model features, y.csv the questionnaire-derived target.
Requires: ctgan==0.11.1, torch, scikit-learn==1.6.1."""
import sys,json,time,warnings,random
warnings.filterwarnings("ignore")
import numpy as np,pandas as pd,torch
from ctgan import CTGAN
from sklearn.model_selection import RepeatedKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error as mae, mean_squared_error as mse, r2_score as r2
D=sys.argv[1]; EPOCHS=int(sys.argv[2]); NFOLDS=int(sys.argv[3]) if len(sys.argv)>3 else 15
X=pd.read_csv(f"{D}/X.csv"); y=pd.read_csv(f"{D}/y.csv").iloc[:,0]
P=dict(n_estimators=149,max_depth=5,max_features=1.0,max_samples=0.8,min_samples_leaf=2,min_samples_split=5,random_state=42,n_jobs=2)
DISC=["usage_frequency_encoded","usage_time_encoded","age_group_encoded","study_year_encoded","experience_encoded"]
SC=["independent_learning_score","verification_score","metacognition_score","learning_benefit_score"]
out=[];t0=time.time()
for k,(tr,te) in enumerate(RepeatedKFold(n_splits=5,n_repeats=3,random_state=42).split(X),1):
    if k>NFOLDS: break
    Xtr,ytr,Xte,yte=X.iloc[tr],y.iloc[tr],X.iloc[te],y.iloc[te]
    base=RandomForestRegressor(**P).fit(Xtr,ytr).predict(Xte)
    train=Xtr.copy(); train["overreliance_score"]=ytr.values            # generator sees TRAINING rows only
    torch.manual_seed(42+k); np.random.seed(42+k); random.seed(42+k)
    g=CTGAN(epochs=EPOCHS,batch_size=50,pac=10,verbose=False,enable_gpu=False); g.fit(train,discrete_columns=DISC)
    syn=g.sample(len(train))
    for c in SC+["overreliance_score"]: syn[c]=syn[c].clip(1,5)
    for c in DISC: syn[c]=syn[c].round().clip(X[c].min(),X[c].max())
    Xa=pd.concat([Xtr,syn[X.columns]],ignore_index=True); ya=pd.concat([ytr,syn["overreliance_score"]],ignore_index=True)
    aug=RandomForestRegressor(**P).fit(Xa,ya).predict(Xte)
    for n,p in (("Real data only",base),("CTGAN-augmented",aug)):
        out.append(dict(Fold=k,Model=n,MAE=mae(yte,p),RMSE=mse(yte,p)**.5,R2=r2(yte,p),n_train=len(Xtr),n_synth=len(syn) if n!="Real data only" else 0))
    print(k,round(time.time()-t0),flush=True)
df=pd.DataFrame(out); df.to_csv(f"{D}/gan249_folds_e{EPOCHS}.csv",index=False)
s=df.groupby("Model")[["MAE","RMSE","R2"]].agg(["mean","std"]).round(4); print(s.to_string())
json.dump({m:{c:round(float(df[df.Model==m][c].mean()),4) for c in("MAE","RMSE","R2")}|{c+"_sd":round(float(df[df.Model==m][c].std()),4) for c in("MAE","RMSE","R2")} for m in df.Model.unique()}|{"epochs":EPOCHS,"folds":int(df.Fold.nunique())},open(f"{D}/gan249_summary_e{EPOCHS}.json","w"),indent=1)
