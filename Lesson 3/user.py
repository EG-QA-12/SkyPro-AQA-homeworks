class User:
    age=0

    def __init__(self,name):
        print("я создался")
        self.username = name

    def sayname (self):
            print("меня зовут", self.username)
            
    def sayage(self):
         print(self.age)
         
    def setAge(self,newAge):
         self.age = newAge
