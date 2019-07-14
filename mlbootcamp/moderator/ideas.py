def areas(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def area(box):
    return (box[:, 2] - box[:, 0]) * (box[:, 3] - box[:, 1])


def al(box):
    return box[:, 2] - box[:, 0]


def aw(box):
    return box[:, 3] - box[:, 1]


def als(box):
    return box[2] - box[0]


def aws(box):
    return box[3] - box[1]


def intersection_over_union(boxes):
    assert (len(boxes) == 8)
    boxA = boxes[:4].values
    boxB = boxes[4:].values

    boxAArea = areas(boxA)
    boxBArea = areas(boxB)

    if (boxAArea == 0 or boxBArea == 0):
        return 0

    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

