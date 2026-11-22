"""Deep Learning vs Random Forest on the 249-response modelling data (research record; not used by the app).
Usage: python dl_249.py <folder with X.csv and y.csv>   Requires tensorflow-cpu==2.20.0."""
import os,sys,json,random,warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
import numpy as np,pandas as pd,tensorflow as tf
from sklearn.model_selection import RepeatedKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error as mae, mean_squared_error as mse, r2_score as r2
warnings.filterwarnings("ignore")
D=sys.argv[1]; SEED=42
random.seed(SEED); np.random.seed(SEED); tf.keras.utils.set_random_seed(SEED)
X=pd.read_csv(f"{D}/X.csv"); y=pd.read_csv(f"{D}/y.csv").iloc[:,0]
P=dict(n_estimators=149,max_depth=5,max_features=1.0,max_samples=0.8,min_samples_leaf=2,min_samples_split=5,random_state=42,n_jobs=2)
def build(d):
    m=tf.keras.Sequential([tf.keras.layers.Input(shape=(d,)),
     tf.keras.layers.Dense(32,activation="relu",kernel_regularizer=tf.keras.regularizers.l2(0.01)),tf.keras.layers.Dropout(0.20),
     tf.keras.layers.Dense(16,activation="relu",kernel_regularizer=tf.keras.regularizers.l2(0.01)),tf.keras.layers.Dropout(0.10),
     tf.keras.layers.Dense(8,activation="relu"),tf.keras.layers.Dense(1,activation="linear")])
    m.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),loss="mse",metrics=["mae"]); return m
res=[]
for k,(tr,te) in enumerate(RepeatedKFold(n_splits=5,n_repeats=3,random_state=SEED).split(X),1):
    rp=RandomForestRegressor(**P).fit(X.iloc[tr],y.iloc[tr]).predict(X.iloc[te])
    sc=StandardScaler(); a=sc.fit_transform(X.iloc[tr]); b=sc.transform(X.iloc[te])
    tf.keras.backend.clear_session(); m=build(9)
    m.fit(a,y.iloc[tr].to_numpy(),validation_split=0.2,epochs=150,batch_size=16,verbose=0,shuffle=True,
      callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss",patience=15,restore_best_weights=True,min_delta=0.0001)])
    dp=m.predict(b,verbose=0).reshape(-1)
    for n,p in (("Random Forest",rp),("Deep Learning",dp)):
        res.append(dict(Fold=k,Model=n,MAE=mae(y.iloc[te],p),RMSE=mse(y.iloc[te],p)**.5,R2=r2(y.iloc[te],p)))
    print(k,flush=True)
df=pd.DataFrame(res); df.to_csv(f"{D}/dl249_folds.csv",index=False)
s=df.groupby("Model")[["MAE","RMSE","R2"]].agg(["mean","std"]).round(4); print(s.to_string())
json.dump({m:{c:round(float(df[df.Model==m][c].mean()),4) for c in("MAE","RMSE","R2")} | {c+"_sd":round(float(df[df.Model==m][c].std()),4) for c in("MAE","RMSE","R2")} for m in df.Model.unique()},open(f"{D}/dl249_summary.json","w"),indent=1)
