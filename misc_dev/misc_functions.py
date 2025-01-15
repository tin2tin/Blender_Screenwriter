import bpy

def get_mergables(areas):
    xs, ys = dict(), dict()
    for a in areas:
        xs[a.x] = a
        ys[a.y] = a
    for area in reversed(areas):
        tx = area.x + area.width + 1
        ty = area.y + area.height + 1
        if tx in xs and xs[tx].y == area.y and xs[tx].height == area.height:
            return area, xs[tx]
        elif ty in ys and ys[ty].x == area.x and ys[ty].width == area.width:
            return area, ys[ty]
    return None, None


def teardown(context):
    while len(context.screen.areas) > 1:
        a, b = get_mergables(context.screen.areas)
        if a and b:
            bpy.ops.screen.area_join(cursor=(a.x, a.y))  #,max_x=b.x,max_y=b.y)
            area = context.screen.areas[0]
            region = area.regions[0]
            blend_data = context.blend_data
            bpy.ops.screen.screen_full_area(
                dict(
                    screen=context.screen,
                    window=context.window,
                    region=region,
                    area=area,
                    blend_data=blend_data))
            bpy.ops.screen.back_to_previous(
                dict(
                    screen=context.screen,
                    window=context.window,
                    region=region,
                    area=area,
                    blend_data=blend_data))


def split_area(window,
               screen,
               region,
               area,
               xtype,
               direction="VERTICAL",
               factor=0.5,
               mouse_x=-100,
               mouse_y=-100):
    beforeptrs = set(list((a.as_pointer() for a in screen.areas)))
    bpy.ops.screen.area_split(
        dict(region=region, area=area, screen=screen, window=window),
        direction=direction,
        factor=factor)
    afterptrs = set(list((a.as_pointer() for a in screen.areas)))
    newareaptr = list(afterptrs - beforeptrs)
    newarea = area_from_ptr(newareaptr[0])
    newarea.type = xtype
    return newarea


def area_from_ptr(ptr):
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.as_pointer() == ptr:
                return area