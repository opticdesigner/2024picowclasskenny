
def input_data()->tuple[int,int]:#def input_data()
    while True:
        try:    
            cm = int(input("請輸入身高(公分):"))
            if cm > 300:
                    raise Exception("超過300公分")
            break
        except ValueError:
            print('輸入格式錯誤')
            continue
        except Exception as e:
            print(f'輸入錯誤{cm}')
            continue
    while True:
        try:    
            kg = int(input("請輸入體重(公斤):"))
            if kg > 300:
                raise Exception("超過300公分")
            break
        except ValueError:
            print('輸入格式錯誤')
            continue
        except Exception as e:
            print(f'輸入錯誤{kg}')
            continue
    return (cm,kg) #傳出cm,kg 2值 or return cm,kg

def get_status(bmi:float)->str:#def get_status(bmi)
    if bmi >=35:
        return "重度肥胖：BMI≧35"
    elif bmi >=30:
        return "中度肥胖：30≦BMI"
    elif bmi >=27:
        return "輕度肥胖：27≦BMI"
    elif bmi >=24:
        return "過重"
    elif bmi >=18.5:
        return "正常範圍"
    else:
        return "體重過輕"
def calculate_bmi(kg:int,cm:int)->float:
    cm=(cm/100)*(cm/100)
    BMI=kg/cm
    return BMI



while True:
    kg=0  #清除變數
    cm=0  #清除變數
    cm,kg = input_data() # or (cm,kg) = input_data()
    print(f'身高={cm},體重={kg}')
    #BMI=calculate_bmi(kg,cm)#引述值呼叫,要按順序
    BMI=calculate_bmi(cm=cm,kg=kg)#引述名稱呼叫,可以以不依照順序
    print(f'BMI={BMI}')
    print(get_status(BMI))
    play_again = input("Do you want to continue?(y or n): ")
    if play_again == 'n':
        break
print('程式結束')