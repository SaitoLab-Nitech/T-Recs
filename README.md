# T-Recs

T-Recs is a dynamic taint tracker for detecting information flows in Android apps. For example, T-Recs can be used to find information leaks in Android apps. Our paper is accepted by [SCAM 2022](https://www.ieee-scam.org/2022/#home). Here is a very brief description of how to use T-Recs. If you have any troubles, please feel free to contact us.

## Setup

### Requirements
- Python 3.10 or later
- Python module
    - prettyprinter
    - nose
- Tools (Please run these in your terminal one by one to make sure you have these tools.)
    - adb
    - aapt
    - apktool
    - apksigner

### Key Preparation

Generate a key for T-Recs to sign apks.

#### Steps

1. Generate a private key with keytool

```
$ keytool -genkey -v -keystore <file_name> -alias <key_alias> -keyalg RSA -validity 25
```

2. Specify information of your key like below in run_parser_and_instrumentator.py

```
project.configure_keystore(keystore=<path_to_your_key>,
                           storepass=<keystore_password>,
                           keypass=<key_password>,
                           alias=<key_alias_name>)
```

## Usage

T-Recs analyzes the target app by the following three phases: static bytecode instrumentation, app exercising, and reconstruction.

### 1. Static Bytecode Instrumentation

Open run_parser_and_instrumentator.py and make sure your keystore information is configured.
Run the command below.
When T-Recs finishes successfully, you get <target_apk_name>.pickle in the same directory as your target apk.

```
python run_parser_and_instrumentator.py <path_to_apk>
```

### 2. App Exercising

Open run_exerciser.py, and specify your device to be used.
Run the command below specifying <target_apk_name>.pickle.
When T-Recs finishes successfully, you get SmalienLog.txt in the same directory as your target apk.

```
python run_exerciser.py <path_to_pickle>
```

### 3. Reconstruction

Run the command below specifying <target_apk_name>.pickle.

```
python run_reconstructor.py <path_to_pickle>
```
