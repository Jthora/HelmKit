//
//  UIColor.swift
//  ARAuraFieldVisualizer
//
//  Created by Jordan Trana on 10/23/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import UIKit

func +(color1: UIColor, color2: UIColor) -> UIColor {
    return addColor(color1, with: color2)
}

func *(color: UIColor, multiplier: Double) -> UIColor {
    return multiplyColor(color, by: CGFloat(multiplier))
}

func *(color: UIColor, multiplier: CGFloat) -> UIColor {
    return multiplyColor(color, by: multiplier)
}

func addColor(_ color1: UIColor, with color2: UIColor) -> UIColor {
    var (r1, g1, b1, a1) = (CGFloat(0), CGFloat(0), CGFloat(0), CGFloat(0))
    var (r2, g2, b2, a2) = (CGFloat(0), CGFloat(0), CGFloat(0), CGFloat(0))

    color1.getRed(&r1, green: &g1, blue: &b1, alpha: &a1)
    color2.getRed(&r2, green: &g2, blue: &b2, alpha: &a2)

    // add the components, but don't let them go above 1.0
    return UIColor(red: min(r1 + r2, 1), green: min(g1 + g2, 1), blue: min(b1 + b2, 1), alpha: (a1 + a2) / 2)
}

func multiplyColor(_ color: UIColor, by multiplier: CGFloat) -> UIColor {
    var (r, g, b, a) = (CGFloat(0), CGFloat(0), CGFloat(0), CGFloat(0))
    color.getRed(&r, green: &g, blue: &b, alpha: &a)
    return UIColor(red: r * multiplier, green: g * multiplier, blue: b * multiplier, alpha: a)
}

extension UIColor {
    
    func inverseColor() -> UIColor {
        var alpha: CGFloat = 1.0

        var white: CGFloat = 0.0
        if self.getWhite(&white, alpha: &alpha) {
            return UIColor(white: 1.0 - white, alpha: alpha)
        }

        var hue: CGFloat = 0.0, saturation: CGFloat = 0.0, brightness: CGFloat = 0.0
        if self.getHue(&hue, saturation: &saturation, brightness: &brightness, alpha: &alpha) {
            return UIColor(hue: 1.0 - hue, saturation: 1.0 - saturation, brightness: 1.0 - brightness, alpha: alpha)
        }

        var red: CGFloat = 0.0, green: CGFloat = 0.0, blue: CGFloat = 0.0
        if self.getRed(&red, green: &green, blue: &blue, alpha: &alpha) {
            return UIColor(red: 1.0 - red, green: 1.0 - green, blue: 1.0 - blue, alpha: alpha)
        }

        return self
    }
    
    /**
     - Parameters:
        - opacity: Can set the opacity of the color.
     
     - Returns: A color that is almost black.
    */
    public class func tmoBlack(withOpacity opacity: CGFloat = 1.0) -> UIColor {
        return UIColor(white: 3/255, alpha: opacity)
    }
    /**
     The T-Mobile Magenta color #E20074
     - Parameters:
        - opacity: Can set the opacity of the color.
     
     - Returns: The T-Mobile Magenta color.
    */
    public class func tmoMagenta(withOpacity opacity: CGFloat = 1.0) -> UIColor {
        return UIColor(red: 226/255, green: 0/255, blue: 116/255, alpha: opacity)
    }
    
    public static var tmoMagenta: UIColor = {
        return UIColor(red: 226/255, green: 0/255, blue: 116/255, alpha: 1)
    }()
    
    public static var tmoHotPink: UIColor = {
        return UIColor.hexColor(hexString: "#fb1aee")!
    }()
    
    /**
     - Returns: A T-Mobile brand gray.
    */
    public class func tmoGray() -> UIColor {
        return UIColor(white: 106/255, alpha: 1)
    }

    static public let tMobileCardTitleColor = UIColor.black
    static public let tMobileCardTextColor = UIColor(red: 181.0/255.0, green: 181.0/255.0, blue: 181.0/255.0, alpha: 1.0)
    static public let tMobileCardDefaultBackground = UIColor(red: 229.0/255.0, green: 229.0/255.0, blue: 229.0/255.0, alpha: 1.0)
    static public let tMobileCardDefaultCTABackground = UIColor(red: 216.0/255.0, green: 216.0/255.0, blue: 216.0/255.0, alpha: 1.0)

    /**
     A hex processor used to determine color sent as a hex string.
     
     - Parameters:
        - hexString: A string starting with # and containing either 6 or 8 hex characters.
     
     - Returns: UIColor with opacity (if provided 8 characters) or with 100% opacity (if provided 6 characters)
    */
    public class func hexColor(hexString: String) -> UIColor? {
        let rValue, gValue, bValue, aValue: CGFloat
        
        if hexString.hasPrefix("#") {
            let start = hexString.index(hexString.startIndex, offsetBy: 1)
            let hexColor = String(hexString[start...])
            
            if hexColor.count == 8 {
                let scanner = Scanner(string: hexColor)
                var hexNumber: UInt64 = 0
                
                if scanner.scanHexInt64(&hexNumber) {
                    aValue = CGFloat((hexNumber & 0xff000000) >> 24) / 255
                    rValue = CGFloat((hexNumber & 0x00ff0000) >> 16) / 255
                    gValue = CGFloat((hexNumber & 0x0000ff00) >> 8) / 255
                    bValue = CGFloat(hexNumber & 0x000000ff) / 255
                    
                    return UIColor.init(red: rValue, green: gValue, blue: bValue, alpha: aValue)
                    
                }
            } else if hexColor.count == 6 {
                let scanner = Scanner(string: hexColor)
                var hexNumber: UInt64 = 0
                
                if scanner.scanHexInt64(&hexNumber) {
                    rValue = CGFloat((hexNumber & 0x00ff0000) >> 16) / 255
                    gValue = CGFloat((hexNumber & 0x0000ff00) >> 8) / 255
                    bValue = CGFloat(hexNumber & 0x000000ff) / 255
                    
                    return UIColor.init(red: rValue, green: gValue, blue: bValue, alpha: 1)
                }
            }
        }
        
        return nil
    }
}

