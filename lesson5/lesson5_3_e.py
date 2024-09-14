import tools

while True:
    kg=0  #清除變數
    cm=0  #清除變數
    cm,kg = tools.input_data() # or (cm,kg) = input_data()

    print(f'身高={cm},體重={kg}')
    #BMI=calculate_bmi(kg,cm)#引述值呼叫,要按順序
    BMI=tools.calculate_bmi(cm=cm,kg=kg)#引述名稱呼叫,可以以不依照順序
    print(f'BMI={BMI}')
    print(tools.get_status(BMI))

    play_again = input("Do you want to continue?(y or n): ")
    if play_again == 'n':
        break
print('程式結束')