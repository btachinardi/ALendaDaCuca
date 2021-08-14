import math
import cave


class MathUtils:
    _radiansToDegree = 57.2957795

    """
    Converts radians into degrees
    """
    def rad2deg(radians):
        return radians * MathUtils._radiansToDegree

    """
    Converts degrees into radians
    """
    def deg2rad(degrees):
        return degrees / MathUtils._radiansToDegree

    """
    Gets the angle around the Z axis for this vector, this is the angle when you are looking from forward to back
    """
    def angle(vector):
        return MathUtils.rad2deg(math.atan2(vector.y, vector.x))

    """
    Gets the angle around the Z axis between two vectors, this is the angle when you are looking from forward to back
    """
    def angleBetween(origin, target):
        return MathUtils.rad2deg(math.atan2(target.y - origin.y, target.x - origin.x))

    """
    Gets the angle around the X axis between two vectors, this is the angle when you are looking from left to right
    """
    def angleBetweenYZ(origin, target):
        return MathUtils.rad2deg(math.atan2(target.y - origin.y, target.z - origin.z))

    """
    Gets the angle around the Y axis between two vectors, this is the angle when you are looking from left to right
    """
    def angleBetweenZX(origin, target):
        return 360 - MathUtils.rad2deg(math.atan2(target.z - origin.z, target.x - origin.x))

    """
    Gets the vector that rotates around the Y axis with the target angle, resulting in X,Z components while Y is 0.

    Rotation always start at the right of the object (looking from down to up) and rotates counter-clockwise
    """
    def deg2vecXZ(degrees):
        radians = MathUtils.deg2rad(degrees)
        return cave.Vector3(math.sin(radians), 0, math.cos(radians))

    """
    Gets the vector that rotates around the X axis with the target angle, resulting in Y,Z components while X is 0.

    Rotation always start at the right of the object (looking from left to right) and rotates counter-clockwise
    """
    def deg2vecYZ(degrees):
        radians = MathUtils.deg2rad(degrees)
        return cave.Vector3(0, math.sin(radians), math.cos(radians))

    """
    Gets the vector that rotates around the Z axis with the target angle, resulting in X,Y components while Z is 0.

    Rotation always start at the right of the object (looking from forward to back) and rotates counter-clockwise
    """
    def deg2vec(degrees):
        radians = MathUtils.deg2rad(degrees)
        return cave.Vector3(math.cos(radians), math.sin(radians), 0)

    def lerp(start, end, time):
        return (end - start) * time + start

    def applyMatrix(matrix, vector):
        result = MathUtils.dotProduct(
            matrix, [[vector.x, vector.y, vector.z, 1]])
        return cave.Vector3(result[0] / result[3], result[1] / result[3], result[2] / result[3])

    def dotProduct(matrixA, matrixB):
        result = []

    def absolute(value):
        return value if value >= 0 else -value

    def normalize(min, max, value):
        return MathUtils.clamp01((value - min) / (max - min))

    def clamp01(value):
        return MathUtils.clamp(0, 1, value)

    def clamp(min, max, value):
        if value <= min:
            return min
        if value >= max:
            return max
        return value
