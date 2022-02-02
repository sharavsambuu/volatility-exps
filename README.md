
# About

    Volatility related experiments



# References and links

    - https://hanguk-quant.medium.com/volatility-targeting-boost-your-quant-day-trading-capital-with-risk-management-94a4e738f65d
    - https://stackoverflow.com/questions/65901162/how-can-i-run-pyqt5-on-my-mac-with-m1chip


# Issues to work around M1

    - https://stackoverflow.com/questions/66081709/whats-the-proposed-way-to-switch-to-native-homebrew-on-m1-macbooks
    - https://stackoverflow.com/questions/65901162/how-can-i-run-pyqt5-on-my-mac-with-m1chip



```shell

    iarch_name="$(uname -m)"
    if [ "${arch_name}" = "x86_64" ]; then
        if [ "$(sysctl -in sysctl.proc_translated)" = "1" ]; then
            echo "Running on Rosetta 2"
        else
            echo "Running on native Intel"
        fi
        eval "$(arch -x86_64 /usr/local/Homebrew/bin/brew shellenv)"
        alias ibrew='arch -x86_64 /usr/local/Homebrew/bin/brew'
    elif [ "${arch_name}" = "arm64" ]; then
        echo "Running on ARM"
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo "Unknown architecture: ${arch_name}"
    fi
    
```
