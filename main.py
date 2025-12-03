from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.popup import Popup
from kivy.core.window import Window
import math
import random

class SimpleRectPacker:
    """مكتبة داخلية لتكديس المستطيلات"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rectangles = []
        self.free_rects = [(0, 0, width, height)]
    
    def add_rect(self, width, height, rid=None):
        """إضافة مستطيل جديد"""
        best_rect = None
        best_score = float('inf')
        
        for free_rect in self.free_rects[:]:
            fx, fy, fw, fh = free_rect
            
            if width <= fw and height <= fh:
                score = min(fw - width, fh - height)
                if score < best_score:
                    best_score = score
                    best_rect = (fx, fy, width, height)
            
            if height <= fw and width <= fh:
                score = min(fw - height, fh - width)
                if score < best_score:
                    best_score = score
                    best_rect = (fx, fy, height, width)
        
        if best_rect:
            x, y, w, h = best_rect
            self.rectangles.append((x, y, w, h, rid))
            self.update_free_rects(x, y, w, h)
            return True
        
        return False
    
    def update_free_rects(self, x, y, w, h):
        """تحديث المساحات الحرة"""
        new_free_rects = []
        
        for fx, fy, fw, fh in self.free_rects:
            if not (x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy):
                if fx < x:
                    new_free_rects.append((fx, fy, x - fx, fh))
                if fx + fw > x + w:
                    new_free_rects.append((x + w, fy, fx + fw - x - w, fh))
                if fy < y:
                    new_free_rects.append((fx, fy, fw, y - fy))
                if fy + fh > y + h:
                    new_free_rects.append((fx, y + h, fw, fy + fh - y - h))
            else:
                new_free_rects.append((fx, fy, fw, fh))
        
        self.free_rects = new_free_rects
    
    def get_rectangles(self):
        return self.rectangles


class DrawingCanvas(FloatLayout):
    """منطقة الرسم"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boards = []
        self.current_board = 0
        self.bind(size=self.redraw, pos=self.redraw)
    
    def set_boards(self, boards):
        self.boards = boards
        self.current_board = 0
        self.redraw()
    
    def redraw(self, *args):
        self.canvas.clear()
        
        if not self.boards or self.current_board >= len(self.boards):
            with self.canvas:
                Color(0.5, 0.5, 0.5)
                self.canvas.add(Rectangle(pos=self.pos, size=self.size))
            return
        
        board = self.boards[self.current_board]
        self.draw_board(board)
    
    def draw_board(self, board):
        board_width, board_height = board['board_size']
        
        # حساب التكبير
        scale_x = (self.width - 40) / board_width
        scale_y = (self.height - 40) / board_height
        scale = min(scale_x, scale_y)
        
        scaled_width = board_width * scale
        scaled_height = board_height * scale
        
        start_x = self.x + (self.width - scaled_width) / 2
        start_y = self.y + (self.height - scaled_height) / 2
        
        with self.canvas:
            # رسم حدود اللوح
            Color(0.8, 0.8, 0.8)
            Rectangle(pos=(start_x, start_y), size=(scaled_width, scaled_height))
            
            Color(0, 0, 0)
            Line(rectangle=(start_x, start_y, scaled_width, scaled_height), width=2)
            
            # رسم القطع
            colors_list = [
                (0.6, 0.8, 1), (0.6, 1, 0.6), (1, 1, 0.6),
                (1, 0.6, 0.8), (0.6, 1, 1), (0.9, 0.8, 0.6)
            ]
            
            for i, (x, y, w, h, piece_id) in enumerate(board['rectangles']):
                color = colors_list[i % len(colors_list)]
                
                piece_x = start_x + x * scale
                piece_y = start_y + y * scale
                piece_w = w * scale
                piece_h = h * scale
                
                Color(*color)
                Rectangle(pos=(piece_x, piece_y), size=(piece_w, piece_h))
                
                Color(0, 0, 0.5)
                Line(rectangle=(piece_x, piece_y, piece_w, piece_h), width=1.5)
    
    def next_board(self):
        if self.boards and self.current_board < len(self.boards) - 1:
            self.current_board += 1
            self.redraw()
    
    def prev_board(self):
        if self.boards and self.current_board > 0:
            self.current_board -= 1
            self.redraw()


class CuttingOptimizerApp(App):
    
    def build(self):
        self.pieces = []
        self.layout_result = []
        
        # التخطيط الرئيسي
        main_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        
        # الجانب الأيسر - الإدخال
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.35, 1), spacing=10)
        
        # أبعاد اللوح
        left_panel.add_widget(Label(text='أبعاد اللوح', size_hint_y=None, height=40, bold=True))
        
        board_layout = GridLayout(cols=2, size_hint_y=None, height=100, spacing=5)
        board_layout.add_widget(Label(text='العرض:'))
        self.board_width_input = TextInput(text='1200', multiline=False, input_filter='float')
        board_layout.add_widget(self.board_width_input)
        
        board_layout.add_widget(Label(text='الارتفاع:'))
        self.board_height_input = TextInput(text='800', multiline=False, input_filter='float')
        board_layout.add_widget(self.board_height_input)
        
        left_panel.add_widget(board_layout)
        
        # إضافة القطع
        left_panel.add_widget(Label(text='إضافة القطع', size_hint_y=None, height=40, bold=True))
        
        piece_layout = GridLayout(cols=2, size_hint_y=None, height=150, spacing=5)
        piece_layout.add_widget(Label(text='عرض القطعة:'))
        self.piece_width_input = TextInput(multiline=False, input_filter='float')
        piece_layout.add_widget(self.piece_width_input)
        
        piece_layout.add_widget(Label(text='ارتفاع القطعة:'))
        self.piece_height_input = TextInput(multiline=False, input_filter='float')
        piece_layout.add_widget(self.piece_height_input)
        
        piece_layout.add_widget(Label(text='الكمية:'))
        self.piece_qty_input = TextInput(text='1', multiline=False, input_filter='int')
        piece_layout.add_widget(self.piece_qty_input)
        
        left_panel.add_widget(piece_layout)
        
        # زر إضافة
        add_btn = Button(text='➕ إضافة قطعة', size_hint_y=None, height=50,
                        background_color=(0.2, 0.8, 0.2, 1))
        add_btn.bind(on_press=self.add_piece)
        left_panel.add_widget(add_btn)
        
        # قائمة القطع
        left_panel.add_widget(Label(text='القطع المضافة:', size_hint_y=None, height=30))
        
        self.pieces_list = Label(text='لا توجد قطع', size_hint_y=0.3, 
                                text_size=(None, None), halign='left', valign='top')
        scroll = ScrollView(size_hint_y=0.3)
        scroll.add_widget(self.pieces_list)
        left_panel.add_widget(scroll)
        
        # أزرار التحكم
        control_layout = GridLayout(cols=2, size_hint_y=None, height=100, spacing=5)
        
        optimize_btn = Button(text='🔄 تحسين', background_color=(0.2, 0.4, 0.8, 1))
        optimize_btn.bind(on_press=self.optimize_layout)
        control_layout.add_widget(optimize_btn)
        
        clear_btn = Button(text='🗑️ مسح', background_color=(0.8, 0.2, 0.2, 1))
        clear_btn.bind(on_press=self.clear_all)
        control_layout.add_widget(clear_btn)
        
        left_panel.add_widget(control_layout)
        
        main_layout.add_widget(left_panel)
        
        # الجانب الأيمن - النتائج والرسم
        right_panel = BoxLayout(orientation='vertical', spacing=10)
        
        # منطقة النتائج
        right_panel.add_widget(Label(text='النتائج', size_hint_y=None, height=40, bold=True))
        
        self.results_label = Label(text='لا توجد نتائج بعد', size_hint_y=0.2,
                                  text_size=(None, None), halign='left', valign='top')
        results_scroll = ScrollView(size_hint_y=0.2)
        results_scroll.add_widget(self.results_label)
        right_panel.add_widget(results_scroll)
        
        # منطقة الرسم
        right_panel.add_widget(Label(text='الرسم البصري', size_hint_y=None, height=40, bold=True))
        
        self.canvas_widget = DrawingCanvas(size_hint_y=0.6)
        right_panel.add_widget(self.canvas_widget)
        
        # أزرار التنقل
        nav_layout = BoxLayout(size_hint_y=None, height=60, spacing=5)
        
        prev_btn = Button(text='◀️ السابق')
        prev_btn.bind(on_press=lambda x: self.canvas_widget.prev_board())
        nav_layout.add_widget(prev_btn)
        
        self.board_label = Label(text='لوح 0 من 0')
        nav_layout.add_widget(self.board_label)
        
        next_btn = Button(text='التالي ▶️')
        next_btn.bind(on_press=lambda x: self.canvas_widget.next_board())
        nav_layout.add_widget(next_btn)
        
        right_panel.add_widget(nav_layout)
        
        main_layout.add_widget(right_panel)
        
        return main_layout
    
    def add_piece(self, instance):
        try:
            width = float(self.piece_width_input.text)
            height = float(self.piece_height_input.text)
            qty = int(self.piece_qty_input.text)
            
            if width <= 0 or height <= 0 or qty <= 0:
                self.show_popup('خطأ', 'يرجى إدخال قيم صحيحة')
                return
            
            for _ in range(qty):
                self.pieces.append((width, height))
            
            self.update_pieces_list()
            
            self.piece_width_input.text = ''
            self.piece_height_input.text = ''
            self.piece_qty_input.text = '1'
            
        except ValueError:
            self.show_popup('خطأ', 'يرجى إدخال أرقام صحيحة')
    
    def update_pieces_list(self):
        if not self.pieces:
            self.pieces_list.text = 'لا توجد قطع'
            return
        
        text = f'إجمالي القطع: {len(self.pieces)}\n\n'
        piece_dict = {}
        
        for w, h in self.pieces:
            key = (w, h)
            piece_dict[key] = piece_dict.get(key, 0) + 1
        
        for (w, h), count in piece_dict.items():
            text += f'{w:.0f} × {h:.0f} : {count} قطعة\n'
        
        self.pieces_list.text = text
    
    def optimize_layout(self, instance):
        try:
            board_width = float(self.board_width_input.text)
            board_height = float(self.board_height_input.text)
            
            if board_width <= 0 or board_height <= 0:
                self.show_popup('خطأ', 'يرجى إدخال أبعاد صحيحة')
                return
            
            if not self.pieces:
                self.show_popup('خطأ', 'يرجى إضافة قطع أولاً')
                return
            
            self.layout_result = self.pack_pieces(board_width, board_height, self.pieces)
            self.display_results()
            self.canvas_widget.set_boards(self.layout_result)
            self.update_board_label()
            
        except ValueError:
            self.show_popup('خطأ', 'يرجى إدخال أرقام صحيحة')
    
    def pack_pieces(self, board_width, board_height, pieces):
        boards = []
        remaining_pieces = pieces.copy()
        remaining_pieces.sort(key=lambda x: x[0] * x[1], reverse=True)
        
        while remaining_pieces:
            packer = SimpleRectPacker(board_width, board_height)
            board_pieces = []
            pieces_to_remove = []
            
            for i, (width, height) in enumerate(remaining_pieces):
                if packer.add_rect(width, height, len(board_pieces)):
                    board_pieces.append((width, height))
                    pieces_to_remove.append(i)
                elif packer.add_rect(height, width, len(board_pieces)):
                    board_pieces.append((height, width))
                    pieces_to_remove.append(i)
            
            for i in reversed(pieces_to_remove):
                remaining_pieces.pop(i)
            
            rectangles = packer.get_rectangles()
            boards.append({
                'pieces': board_pieces,
                'rectangles': rectangles,
                'board_size': (board_width, board_height)
            })
            
            if not pieces_to_remove:
                break
        
        return boards
    
    def display_results(self):
        if not self.layout_result:
            self.results_label.text = 'لا توجد نتائج'
            return
        
        total_pieces = len(self.pieces)
        placed_pieces = sum(len(board['pieces']) for board in self.layout_result)
        board_area = float(self.board_width_input.text) * float(self.board_height_input.text)
        
        text = f'📊 النتائج:\n\n'
        text += f'إجمالي القطع: {total_pieces}\n'
        text += f'القطع المرتبة: {placed_pieces}\n'
        text += f'عدد الألواح: {len(self.layout_result)}\n\n'
        
        for i, board in enumerate(self.layout_result):
            used_area = sum(w * h for w, h in board['pieces'])
            efficiency = (used_area / board_area) * 100
            text += f'لوح {i+1}: {len(board["pieces"])} قطعة ({efficiency:.1f}%)\n'
        
        self.results_label.text = text
    
    def update_board_label(self):
        if self.layout_result:
            current = self.canvas_widget.current_board + 1
            total = len(self.layout_result)
            self.board_label.text = f'لوح {current} من {total}'
        else:
            self.board_label.text = 'لوح 0 من 0'
    
    def clear_all(self, instance):
        self.pieces = []
        self.layout_result = []
        self.update_pieces_list()
        self.results_label.text = 'لا توجد نتائج'
        self.canvas_widget.set_boards([])
        self.update_board_label()
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message),
                     size_hint=(0.8, 0.3))
        popup.open()


if __name__ == '__main__':
    CuttingOptimizerApp().run()
