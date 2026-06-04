# **Option Chain Market**

### **What is an Option?**

An option is a financial contract that gives the buyer the right, but not the obligation, to buy or sell an underlying asset at a predetermined price before expiry.<br>

**Call Option (CE) :** A Call Option (CE) generally benefits when the market moves upward. Traders buy calls when they expect NIFTY50 to rise.
<br>

**Put Option (PE) :** A Put Option (PE) generally benefits when the market moves downward. Traders buy puts when they expect NIFTY50 to fall.
<br></br>

### **What is NIFTY50?**

NIFTY50 is the benchmark stock market index of the National Stock Exchange (NSE) of India. It represents the performance of 50 major companies listed on NSE and is one of the most actively traded indices in India. The spot price displayed in the terminal represents the current value of the NIFTY50 index.
<br></br>

### **What is an Expiry Date?**

Every option contract has a fixed expiry date. After expiry, the option contract becomes invalid and ceases to trade. The terminal displays the currently selected expiry date so users always know which option series they are analyzing.
<br></br>

### **What is an Option Chain?**

An option chain is a complete list of available option contracts for a specific expiry.

It contains:&emsp; **Strike Prices**<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**Call Options (CE)**<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**Put Options (PE)**<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**Open Interest (OI)**<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**Price Data**<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;**Volume Data**<br>

The option chain is one of the most important tools used by traders and institutions to assess market sentiment and positioning.
<br></br>

### **What is LTP?**

LTP stands for Last Traded Price. It represents the most recent traded price of a particular option contract. A rising LTP indicates increasing option value, while a falling LTP indicates decreasing option value.
<br></br>

### **What is Open Interest (OI)?**

Open Interest (OI) represents the total number of active option contracts currently open in the market. Higher OI generally indicates greater participation and liquidity.<br>
CE OI (Call Open Interest)<br>
PE OI (Put Open Interest)
<br></br>

### **What is Delta OI (ΔOI)?**

Delta OI represents the change in Open Interest since the previous observation. It helps traders understand whether new positions are being created or existing positions are being closed. Increasing OI often indicates fresh participation, while decreasing OI often indicates position unwinding.
<br></br>

### **What is PCR?**

PCR (Put-Call Ratio) is calculated as:
PCR = Total Put OI / Total Call OI<br>

Interpretation:<br>
PCR > 1 → More Put OI than Call OI<br>
PCR < 1 → More Call OI than Put OI<br>
Extremely high or low PCR values may indicate crowded market positioning<br>

PCR is commonly used as a sentiment indicator.
<br></br>

The terminal automatically analyzes changes in Option Price (LTP) and Open Interest (OI) to classify market activity into four common option market structures:
1) **Long Buildup:** <span style="color: #26ed65;"><strong>Price ↑</strong></span> and <span style="color: #26ed65;"><strong>OI ↑</strong></span><br>
Fresh long positions are being created, generally considered bullish.<br>
2) **Short Buildup:** <span style="color: #ff4d4d;"><strong>Price ↓</strong></span> and <span style="color: #26ed65;"><strong>OI ↑</strong></span><br>
Fresh short positions are being created, generally considered bearish.<br>
3) **Long Unwinding:** <span style="color: #ff4d4d;"><strong>Price ↓</strong></span> and <span style="color: #ff4d4d;"><strong>OI ↓</strong></span><br>
Existing long positions are being closed, indicates weakening bullish sentiment.<br>
4) **Short Covering:** <span style="color: #26ed65;"><strong>Price ↑</strong></span> and <span style="color: #ff4d4d;"><strong>OI ↓</strong></span><br>
Existing short positions are being closed, indicates weakening bearish sentiment and potential upward movement.<br>