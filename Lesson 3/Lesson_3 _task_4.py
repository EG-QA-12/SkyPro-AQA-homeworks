from turtle import *

my_turtle = Turtle()
my_turtle.speed(0)
my_turtle.screen.setup(1200, 800)

# Нарисовать тело
my_turtle.penup()
my_turtle.goto(-80,0)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.circle(120)
my_turtle.end_fill()

# Нарисовать левое ухо
my_turtle.penup()
my_turtle.goto(-140,220)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.right(45)
my_turtle.circle(100,80)
my_turtle.circle(25,130)
my_turtle.circle(100,80)
my_turtle.end_fill()

# Нарисовать правое ухо
my_turtle.penup()
my_turtle.goto(60,220)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.left(45)
my_turtle.circle(-100,80)
my_turtle.circle(-25,130)
my_turtle.circle(-100,80)
my_turtle.end_fill()

# Нарисовать левый глаз
my_turtle.penup()
my_turtle.goto(-40,80)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("white")
my_turtle.circle(30)
my_turtle.end_fill()

# Нарисовать правый глаз
my_turtle.penup()
my_turtle.goto(50,80)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("white")
my_turtle.circle(30)
my_turtle.end_fill()

# Нарисовать зрачки
my_turtle.penup()
my_turtle.goto(-25,70)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("black")
my_turtle.circle(10)
my_turtle.end_fill()

my_turtle.penup()
my_turtle.goto(65,70)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("black")
my_turtle.circle(10)
my_turtle.end_fill()

# Нарисовать нос
my_turtle.penup()
my_turtle.goto(0,0)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F7BE81")
my_turtle.circle(20)
my_turtle.end_fill()

# Нарисовать рот
my_turtle.penup()
my_turtle.goto(-70,-50)
my_turtle.pendown()
my_turtle.right(90)
my_turtle.circle(70, 180)

# Нарисовать лапы
my_turtle.penup()
my_turtle.goto(-70,-120)
my_turtle.pendown()
my_turtle.right(30)
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.circle(70, 240)
my_turtle.right(150)
my_turtle.forward(140)
my_turtle.right(150)
my_turtle.circle(70, 240)
my_turtle
