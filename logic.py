class BotVision:
    """
    Contient toute la logique mathématique et l'analyse d'image.
    Indépendant de l'interface graphique.
    """

    @staticmethod
    def parse_rgb(string_rgb):
        try:
            return tuple(map(int, string_rgb.split(',')))
        except:
            return (0, 0, 0)

    @staticmethod
    def check_match(c1, c2, tol):
        return (abs(c1[0] - c2[0]) <= tol and
                abs(c1[1] - c2[1]) <= tol and
                abs(c1[2] - c2[2]) <= tol)

    @staticmethod
    def measure_blob_at(pixels, start_x, start_y, w, h, target_rgb, tol):
        # Sécurisation des limites
        start_x = max(0, min(start_x, w - 1))
        start_y = max(0, min(start_y, h - 1))

        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        limit = 100  # Limite de taille max d'un objet

        # Extension gauche
        while min_x > 0 and (start_x - min_x) < limit:
            if not BotVision.check_match(pixels[min_x - 1, start_y], target_rgb, tol): break
            min_x -= 1
        # Extension droite
        while max_x < (w - 1) and (max_x - start_x) < limit:
            if not BotVision.check_match(pixels[max_x + 1, start_y], target_rgb, tol): break
            max_x += 1
        # Extension haut
        while min_y > 0 and (start_y - min_y) < limit:
            if not BotVision.check_match(pixels[start_x, min_y - 1], target_rgb, tol): break
            min_y -= 1
        # Extension bas
        while max_y < (h - 1) and (max_y - start_y) < limit:
            if not BotVision.check_match(pixels[start_x, max_y + 1], target_rgb, tol): break
            max_y += 1

        width = max_x - min_x + 1
        height = max_y - min_y + 1
        return width, height, (min_x, min_y, max_x, max_y)