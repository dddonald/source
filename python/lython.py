#!/usr/bin/env python

from Tkinter import *
import math

GRID_RANGE = 10

def xy_to_cell_coord(x, y, zoom):
      return(math.ceil((x-2) / zoom), math.ceil((y-2) / zoom )) 

def grid_centre(x, y, width, height):
      return(int(x) + (width / 2), int(y) + (height / 2))

def grid_range(x, y, width, height, factor, zoom):
      startx = x - width*factor
      starty = y - height*factor
      endx = x + width*factor
      endy = y + height*factor
      return (startx - startx%zoom + 1, starty - starty%zoom +1, endx, endy)

class LifeCanvas:
    def __init__(self, parent, zoom, width, height):
        self._zoom = zoom
        self._width = width
        self._height = height
        self._engine = LifeEngine(set())

        self._frame = Frame(parent)
        self._frame.pack()

        self._scrollregion = [-GRID_RANGE * width, -GRID_RANGE * height,
                              GRID_RANGE * width, GRID_RANGE * height]

        self._canvas=Canvas(self._frame, scrollregion=self._scrollregion,
                            width=self._width, height=self._height, bg='white')

        self._vertscroll = Scrollbar(self._frame, orient=VERTICAL,
                                     command=self.yscrollbar)
        self._vertscroll.pack(side=RIGHT, fill=Y)

        self._canvas.pack()        

        self._horiscroll = Scrollbar(self._frame, orient=HORIZONTAL,
                                     command=self.xscrollbar)
        self._horiscroll.pack(fill=X)        
        
        self._canvas.config(xscrollcommand=self._horiscroll.set,
                            yscrollcommand=self._vertscroll.set)
        
        self._canvas.bind("<ButtonRelease-1>", self.select_cell)

    def xscrollbar(self, arg1, arg2, arg3):
        x,y = grid_centre(self._canvas.canvasx( 0 ),
                          self._canvas.canvasy( 0 ),
                          self._width, self._height)
        range_width = ( GRID_RANGE-2 ) * self._width

        if self._centrex - range_width < x < self._centrex + range_width:
              pass
        else:
              if int( arg2 ) > 0:
                    self._scrollregion[2] += range_width
              else:
                    self._scrollregion[0] -= range_width

              self._canvas.config( scrollregion=self._scrollregion )
              self.redraw()

        self._canvas.xview(arg1, arg2, arg3)

    def yscrollbar(self, arg1, arg2, arg3):
        x,y = grid_centre(self._canvas.canvasx( 0 ),
                          self._canvas.canvasy( 0 ),
                          self._width, self._height)

        range_height = ( GRID_RANGE-2 ) * self._height

        if self._centrey - range_height < y < self._centrey + range_height:
              pass
        else:
              if int( arg2 ) > 0:
                    self._scrollregion[3] += range_height
              else:
                    self._scrollregion[1] -= range_height

              self._canvas.config(scrollregion=self._scrollregion)
              self.redraw()

        self._canvas.yview(arg1, arg2, arg3)

    def redraw(self):
        self._canvas.delete(ALL)
        self.draw_grid()
        self.draw_cells(self._engine.get_cells())

    def select_cell(self, event):
        coord = xy_to_cell_coord(self._canvas.canvasx(event.x),
                                 self._canvas.canvasy(event.y), self._zoom)
        colour = 'blue' if self._engine.toggle_cell(coord) else 'white' 
        self.draw_single_cell(coord[0], coord[1], colour)
            
    def set_zoom(self, zoom):
        self._zoom = zoom

    def run_turn(self):
        self.clear_cells(self._engine.get_cells())
        self.draw_cells(self._engine.run_next_turn())

    def draw_grid(self):
        self._centrex, self._centrey = grid_centre(self._canvas.canvasx(0),
                                                   self._canvas.canvasy(0),
                                                   self._width, self._height)
          
        startx, starty, endx, endy = grid_range(self._centrex,
                                                self._centrey,
                                                self._width, self._height,
                                                GRID_RANGE, self._zoom)

        for x in range(startx, endx, self._zoom):
              self._canvas.create_line(x,starty, x, endy)
        for y in range(starty, endy, self._zoom):
              self._canvas.create_line(startx, y, endx, y)

    def draw_single_cell(self, x, y, fillcolour):
        self._canvas.create_rectangle(( x-1 ) * self._zoom + 2,
                                      ( y-1 ) * self._zoom + 2,
                                      x*self._zoom + 1,
                                      y*self._zoom + 1,
                                      fill=fillcolour, width=0 )

    def draw_cells(self, cells):
        for x, y in cells:
            self.draw_single_cell(x, y, 'blue');

    def clear_cells( self, cells ):
        for x, y in cells:
            self.draw_single_cell(x, y, 'white');


class LifeGui:
    def __init__(self, zoom, width, height, timeout):
        self._root = Tk()
        self._zoom = IntVar(self._root)
        self._zoom.set(zoom)
        self._timeout = IntVar(self._root)
        self._timeout.set(timeout)
        self._job = None

        self.initialise(width, height)

    def initialise(self, width, height):
        self._root.title("Lython")

        self._canvas = LifeCanvas(self._root, self._zoom.get(), width, height)

        self._gobutton = Button(self._root, text="GO", command=self.gobutton)
        self._gobutton.pack(side=LEFT)

        self._stepbutton = Button(self._root, text="STEP",
                                  command=self.stepbutton)
        self._stepbutton.pack(side=RIGHT)
        
        self._zoomscale = Scale(self._root, variable=self._zoom, label="Zoom",
                                command=self.zoomadjust, orient=HORIZONTAL,
                                from_=2)
        self._zoomscale.pack(side=LEFT)

        self._timescale = Scale(self._root, variable= self._timeout,
                                label="Time (ms)", command=self.timescale,
                                orient=HORIZONTAL,
                                from_=10, to=2000, resolution=10)
        self._timescale.pack(side=RIGHT)

        self._canvas.redraw()
        mainloop()
        
    def gobutton(self):
        if (self._gobutton["text"] == "GO"):
            self.run_life()
            self._gobutton["text"] = "STOP"
        else:
            self._root.after_cancel(self._job) 
            self._gobutton["text"] = "GO"

    def stepbutton(self):
        self._canvas.run_turn()

    def timescale(self, event):
          if (self._gobutton["text"] == "GO" and self._job ):
                self._root.after_cancel(self._job)
                self.run_life()

    def zoomadjust(self, event):
          self._canvas.set_zoom(self._zoom.get())
          self._canvas.redraw()

    def run_life(self):
        self._canvas.run_turn()
        self._job = self._root.after(self._timeout.get(), self.run_life)
        

class LifeEngine:
    def __init__(self, live_cells):
        self._live_cells = live_cells
        
    def count_live_cells(self, coordx, coordy):
        return sum(1 for x in range(-1, 2) for y in range(-1, 2)
        if not x == y == 0 and (coordx + x, coordy + y) in self._live_cells)

    def comes_alive(self, coordx, coordy):
        live_cells = self.count_live_cells(coordx, coordy)
        if (coordx, coordy) in self._live_cells:
            return live_cells in ( 2, 3 )
        else:
            return live_cells == 3

    def run_next_turn(self):
        adjacent = set()
        for node in self._live_cells:
            [adjacent.add( (x + node[0], y + node[1]))
                  for x in range(-1, 2) for y in range(-1, 2)]
        alivenext = {i for i in adjacent if self.comes_alive(i[0], i[1])}
        self._live_cells = alivenext
        return self._live_cells

    def get_cells(self):
        return self._live_cells

    def toggle_cell(self, coord):
        if coord in self._live_cells:
            self._live_cells.remove(coord)
            return False
        else:
            self._live_cells.add(coord)
            return True

# Main

def main():
    mygui = LifeGui(10, 702, 502, 100)

if __name__ == "__main__":
    main()



