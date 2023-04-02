from turtle import *

my_turtle = Turtle()
my_turtle.speed(0)
my_turtle.screen.setup(1200, 800)

# Нарисовать тело
my_turtle.penup()
my_turtle.goto(-120,-70)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.circle(220)
my_turtle.end_fill()

# Нарисовать левое ухо
my_turtle.penup()
my_turtle.goto(-200,300)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.right(245)
my_turtle.circle(100,80)
my_turtle.circle(35,130)
my_turtle.circle(100,80)
my_turtle.end_fill()

# Нарисовать правое ухо
my_turtle.penup()
my_turtle.goto(60,220)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F5A9D0")
my_turtle.left(50)
my_turtle.circle(-100,80)
my_turtle.circle(-25,130)
my_turtle.circle(-100,80)
my_turtle.end_fill()

# Нарисовать левый глаз
my_turtle.penup()
my_turtle.goto(-190,190)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("white")
my_turtle.circle(30)
my_turtle.end_fill()

# Нарисовать правый глаз
my_turtle.penup()
my_turtle.goto(-25,190)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("white")
my_turtle.circle(30)
my_turtle.end_fill()

# Нарисовать зрачки
my_turtle.penup()
my_turtle.goto(-32,170)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("black")
my_turtle.circle(10)
my_turtle.end_fill()

my_turtle.penup()
my_turtle.goto(-195,170)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("black")
my_turtle.circle(10)
my_turtle.end_fill()

# Нарисовать нос
my_turtle.penup()
my_turtle.goto(-110,100)
my_turtle.pendown()
my_turtle.begin_fill()
my_turtle.fillcolor("#F7BE81")
my_turtle.circle(30)
my_turtle.end_fill()

# Нарисовать рот
my_turtle.penup()
my_turtle.goto(-60,45)
my_turtle.pendown()
my_turtle.right(80)
my_turtle.circle(60, -150)

my_turtle.screen.exitonclick()
my_turtle.screen.mainloop()