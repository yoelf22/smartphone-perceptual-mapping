# 🔄 Flexible Column Detection Guide

The upload system now automatically detects product/item name columns with maximum flexibility.

## ✅ **Supported Column Names**

### **Primary Patterns**
- `product_name`, `product`, `phone_model`, `model`
- `brand`, `item`, `name`
- `service`, `app`, `software`, `platform`
- `company`, `manufacturer`

### **Industry-Specific**
- **Tech**: `smartphone`, `mobile`, `device`, `tool`, `system`
- **Business**: `solution`, `option`, `choice`, `alternative`  
- **Automotive**: `car`, `vehicle`
- **Web**: `website`, `platform`

### **Generic Fallback**
- **Any string column** will be used if no keyword matches found
- **First text column** automatically selected

## 🎯 **How It Works**

1. **Exact Match**: Looks for exact column name matches
2. **Partial Match**: Searches within column names (case-insensitive)
3. **Type Fallback**: Uses first string/object column as backup
4. **Auto-Rename**: Internally converts to `phone_model` for compatibility

## 📊 **Example Data Formats**

### **Streaming Services**
```csv
service,category,popularity,content_quality,user_interface,price_value
Netflix,Entertainment,85,9,8,6
Spotify,Music,82,8,9,8
Disney+,Entertainment,78,8,8,5
```

### **Software Products**
```csv
platform,usability,features,performance,support
Slack,8,7,9,8
Teams,7,9,8,7
Zoom,9,8,8,9
```

### **Physical Products**
```csv
model,build_quality,design,value,brand_trust
iPhone 15,9,9,4,9
Samsung S24,8,8,6,8
Pixel 8,7,7,7,7
```

### **Generic Items**
```csv
item,rating_1,rating_2,rating_3,overall
Option A,7,8,6,7
Choice B,8,7,9,8
Alternative C,6,9,7,7
```

## 🚨 **No More Warnings!**

The system now handles:
- ✅ Any product identifier column name
- ✅ Mixed case variations (`Product_Name`, `PRODUCT`, `product`)
- ✅ Industry-specific terminology
- ✅ Generic naming patterns
- ✅ Automatic fallback to string columns

## 💡 **Pro Tips**

1. **Use descriptive names**: `service_name` better than `col1`
2. **Keep it simple**: `product` works just as well as `product_name_identifier`
3. **Industry standard**: Use terms common in your field
4. **Mixed formats OK**: The system handles `Product_Name`, `product-name`, `PRODUCT`

## 🧪 **Test Your Data**

Use `test_flexible_columns.py` to verify your column names work:

```bash
source venv/bin/activate
python test_flexible_columns.py
```

The system is designed to **"just work"** with your existing data structure! 🎉