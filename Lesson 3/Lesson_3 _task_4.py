from turtle import *

# создаем объект черепашки
my_turtle = Turtle()

# настраиваем скорость рисования и размер экрана
my_turtle.speed(0)
my_turtle.screen.setup(800, 600)

# задаем цвет заливки и обводки для черепашки
my_turtle.color("brown", "white")

# рисуем голову кролика
my_turtle.begin_fill()
my_turtle.circle(50)
my_turtle.end_fill()

# рисуем тело кролика
my_turtle.right(90)
my_turtle.forward(100)
my_turtle.right(45)
my_turtle.begin_fill()
my_turtle.circle(50, 180)
my_turtle.right(90)
my_turtle.circle(50, 180)
my_turtle.end_fill()
my_turtle.right(135)
my_turtle.forward(100)

# рисуем уши кролика
my_turtle.right(135)
my_turtle.forward(50)
my_turtle.right(90)
my_turtle.begin_fill()
my_turtle.circle(30, 180)
my_turtle.right(90)
my_turtle.circle(30, 180)
my_turtle.end_fill()
my_turtle.right(90)
my_turtle.forward(50)

# рисуем глаза кролика
my_turtle.penup()
my_turtle.goto(-15, 20)
my_turtle.pendown()
my_turtle.color("black")
my_turtle.begin_fill()
my_turtle.circle(10)
my_turtle.end_fill()
my_turtle.penup()
my_turtle.goto(15, 20)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.circle(10)
my_turtle.end_fill()

# рисуем нос кролика
my_turtle.penup()
my_turtle.goto(0, 0)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.circle(5)
my_turtle.end_fill()

# завершаем работу
my_turtle.screen.exitonclick()
my_turtle.screen.mainloop()

